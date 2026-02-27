import sqlite3
import time
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DATABASE = 'database.db'

# --- Design Pattern: Singleton & Database Wrapper ---
class DBManager:
    """
    Gerencia a conexão com o banco de dados SQLite.
    Garante que as tabelas existam na inicialização.
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Tabela da Partida (Apenas uma linha será usada para o estado atual)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS match_state (
                    id INTEGER PRIMARY KEY,
                    team_a_name TEXT, team_b_name TEXT,
                    logo_a TEXT, logo_b TEXT,
                    score_a INTEGER, score_b INTEGER,
                    status TEXT, -- 1º Tempo, 2º Tempo, etc.
                    stoppage_time INTEGER, -- Em minutos
                    start_timestamp REAL, -- Timestamp do inicio do cronometro
                    accumulated_seconds REAL, -- Segundos acumulados antes da pausa
                    is_running INTEGER -- Booleano (0 ou 1)
                )
            ''')
            # Tabela de Penaltis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS penalties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team TEXT, -- 'A' ou 'B'
                    player_name TEXT,
                    result TEXT -- 'GOL' ou 'PERDIDO'
                )
            ''')
            
            # Inicializa estado padrão se não existir
            cursor.execute('SELECT count(*) FROM match_state')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO match_state (id, team_a_name, team_b_name, logo_a, logo_b, score_a, score_b, status, stoppage_time, start_timestamp, accumulated_seconds, is_running)
                    VALUES (1, 'Time A', 'Time B', '', '', 0, 0, '1º TEMPO', 0, 0, 0, 0)
                ''')
            conn.commit()

# Instância global do gerenciador de DB
db_manager = DBManager(DATABASE)

# --- Model (Lógica de Negócios) ---
class MatchModel:
    """
    Classe responsável por manipular os dados da partida.
    Encapsula a lógica de cálculo de tempo e persistência.
    """
    @staticmethod
    def get_state():
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM match_state WHERE id = 1')
        match = dict(cursor.fetchone())
        
        # Busca penaltis
        cursor.execute('SELECT * FROM penalties ORDER BY id ASC')
        penalties = [dict(row) for row in cursor.fetchall()]
        match['penalties'] = penalties
        
        # Lógica de Tempo do Servidor para evitar desincronia
        current_time = time.time()
        elapsed = match['accumulated_seconds']
        if match['is_running']:
            elapsed += (current_time - match['start_timestamp'])
        
        match['calculated_time_seconds'] = elapsed
        conn.close()
        return match

    @staticmethod
    def update_state(data):
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Tratamento especial para o cronômetro
        if 'action' in data:
            cursor.execute('SELECT start_timestamp, accumulated_seconds, is_running FROM match_state WHERE id = 1')
            row = cursor.fetchone()
            is_running = row['is_running']
            acc_sec = row['accumulated_seconds']
            start_ts = row['start_timestamp']
            
            if data['action'] == 'start' and not is_running:
                cursor.execute('UPDATE match_state SET is_running = 1, start_timestamp = ? WHERE id = 1', (time.time(),))
            elif data['action'] == 'pause' and is_running:
                delta = time.time() - start_ts
                new_acc = acc_sec + delta
                cursor.execute('UPDATE match_state SET is_running = 0, accumulated_seconds = ? WHERE id = 1', (new_acc,))
            elif data['action'] == 'reset_timer':
                cursor.execute('UPDATE match_state SET is_running = 0, accumulated_seconds = 0, start_timestamp = 0 WHERE id = 1')

        # Atualização de campos gerais
        fields = ['team_a_name', 'team_b_name', 'score_a', 'score_b', 'status', 'stoppage_time', 'logo_a', 'logo_b']
        for field in fields:
            if field in data:
                cursor.execute(f'UPDATE match_state SET {field} = ? WHERE id = 1', (data[field],))
        
        conn.commit()
        conn.close()

    @staticmethod
    def add_penalty(team, player, result):
        conn = db_manager.get_connection()
        conn.execute('INSERT INTO penalties (team, player_name, result) VALUES (?, ?, ?)', (team, player, result))
        conn.commit()
        conn.close()

    @staticmethod
    def clear_penalties():
        conn = db_manager.get_connection()
        conn.execute('DELETE FROM penalties')
        conn.commit()
        conn.close()

# --- Rotas (Controllers) ---
@app.route('/')
def route_placar():
    return render_template('placar.html')

@app.route('/admin')
def route_admin():
    return render_template('admin.html')

@app.route('/penaltis')
def route_penaltis():
    return render_template('penaltis.html')

@app.route('/api/match', methods=['GET'])
def get_match():
    return jsonify(MatchModel.get_state())

@app.route('/api/update', methods=['POST'])
def update_match():
    data = request.json
    MatchModel.update_state(data)
    return jsonify({"status": "success"})

@app.route('/api/penalties', methods=['POST', 'DELETE'])
def handle_penalties():
    if request.method == 'POST':
        data = request.json
        MatchModel.add_penalty(data['team'], data['player'], data['result'])
    elif request.method == 'DELETE':
        MatchModel.clear_penalties()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)