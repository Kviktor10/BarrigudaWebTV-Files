/**
 * Classe utilitária para formatação de tempo
 */
class TimeFormatter {
    static format(seconds) {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
}

/**
 * API Service (Camada de Comunicação)
 */
class MatchService {
    static async getState() {
        const response = await fetch('/api/match');
        return await response.json();
    }

    static async update(data) {
        await fetch('/api/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }

    static async addPenalty(data) {
        await fetch('/api/penalties', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }
    
    static async clearPenalties() {
        await fetch('/api/penalties', { method: 'DELETE' });
    }
}

/**
 * Controller Base (Observer Pattern)
 */
class PageController {
    constructor() {
        this.state = {};
        this.init();
    }

    init() {
        // Polling para atualização em tempo real (Alternativa simples a WebSockets)
        this.fetchData();
        setInterval(() => this.fetchData(), 1000);
    }

    async fetchData() {
        const data = await MatchService.getState();
        this.state = data;
        this.render();
    }

    render() {
        throw new Error("Render method must be implemented by subclass");
    }
}

/**
 * 1. Controlador da Página do Placar
 */
class ScoreboardController extends PageController {
    render() {
        // Atualiza Textos
        document.getElementById('teamA').innerText = this.state.team_a_name;
        document.getElementById('teamB').innerText = this.state.team_b_name;
        document.getElementById('score').innerText = `${this.state.score_a} X ${this.state.score_b}`;
        document.getElementById('status').innerText = this.state.status;
        
        // Timer
        const timeStr = TimeFormatter.format(this.state.calculated_time_seconds);
        const stoppageStr = this.state.stoppage_time > 0 ? `+${this.state.stoppage_time}'` : '';
        document.getElementById('timer').innerHTML = `${timeStr} <span class="stoppage">${stoppageStr}</span>`;

        // Logos (Fallback se vazio)
        if(this.state.logo_a) document.getElementById('logoA').src = this.state.logo_a;
        if(this.state.logo_b) document.getElementById('logoB').src = this.state.logo_b;
    }
}

/**
 * 2. Controlador da Página de Admin
 */
class AdminController extends PageController {
    constructor() {
        super();
        this.bindEvents();
    }

    bindEvents() {
        // Exemplo de binding. Em produção, faria para todos os campos.
        document.getElementById('btnUpdateScore').addEventListener('click', () => {
            const sA = document.getElementById('inputScoreA').value;
            const sB = document.getElementById('inputScoreB').value;
            MatchService.update({ score_a: sA, score_b: sB });
        });
        
        document.getElementById('btnStart').addEventListener('click', () => MatchService.update({ action: 'start' }));
        document.getElementById('btnPause').addEventListener('click', () => MatchService.update({ action: 'pause' }));
        document.getElementById('btnResetTime').addEventListener('click', () => MatchService.update({ action: 'reset_timer' }));
        
        document.getElementById('btnUpdateNames').addEventListener('click', () => {
            MatchService.update({
                team_a_name: document.getElementById('inputNameA').value,
                team_b_name: document.getElementById('inputNameB').value,
                status: document.getElementById('inputStatus').value,
                stoppage_time: document.getElementById('inputStoppage').value,
                logo_a: document.getElementById('inputLogoA').value,
                logo_b: document.getElementById('inputLogoB').value
            });
        });

        document.getElementById('btnAddPenalty').addEventListener('click', async () => {
            await MatchService.addPenalty({
                team: document.getElementById('penTeam').value,
                player: document.getElementById('penPlayer').value,
                result: document.getElementById('penResult').value
            });
            this.fetchData(); // Força update imediato
        });

         document.getElementById('btnClearPenalties').addEventListener('click', async () => {
            if(confirm("Limpar todos os pênaltis?")) MatchService.clearPenalties();
        });
    }

    render() {
        // Preenche inputs com valor atual apenas se não estiver focado (para não atrapalhar a digitação)
        if (document.activeElement.tagName !== 'INPUT') {
             document.getElementById('inputScoreA').value = this.state.score_a;
             document.getElementById('inputScoreB').value = this.state.score_b;
             document.getElementById('inputNameA').value = this.state.team_a_name;
             document.getElementById('inputNameB').value = this.state.team_b_name;
             document.getElementById('inputStatus').value = this.state.status;
             document.getElementById('timeDisplay').innerText = TimeFormatter.format(this.state.calculated_time_seconds);
        }
    }
}

/**
 * 3. Controlador da Tabela de Pênaltis
 */
class PenaltyController extends PageController {
    render() {
        const tbody = document.getElementById('penaltyBody');
        tbody.innerHTML = '';
        
        this.state.penalties.forEach((p, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td>${p.team}</td>
                <td>${p.player_name}</td>
                <td class="${p.result === 'GOL' ? 'result-gol' : 'result-perdido'}">${p.result}</td>
            `;
            tbody.appendChild(tr);
        });
    }
}

// Inicialização baseada na página atual
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('scoreboard-view')) new ScoreboardController();
    if (document.getElementById('admin-view')) new AdminController();
    if (document.getElementById('penalty-view')) new PenaltyController();
});