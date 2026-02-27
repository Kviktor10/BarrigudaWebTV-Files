import sqlite3

# ==========================================
# PADRÃO SINGLETON PARA BANCO DE DADOS
# ==========================================
class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect('grade_radio.db', check_same_thread=False)
            cls._instance.conn.row_factory = sqlite3.Row
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        cursor = self.conn.cursor()
        # dias armazena strings como "SEGUNDA" ou "SEGUNDA,TERÇA"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS programas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                horario TEXT NOT NULL,
                nome TEXT NOT NULL,
                dias TEXT NOT NULL,
                categoria TEXT
            )
        ''')
        self.conn.commit()

    def get_conn(self):
        return self.conn

# ==========================================
# SCRIPT DE TRANSFORMAÇÃO E CARGA (SEED)
# ==========================================
def popular_banco():
    db = DatabaseManager().get_conn()
    cursor = db.cursor()

    # Dados processados da sua lista
    dados_programas = [
            ("11h", "Momento Esporte - Irecê", "SEGUNDA", ""),
            ("11h", "Barriguda Notícias", "SEGUNDA", ""),
            ("19h", "De cara com Moisés Cambuy", "SEGUNDA", ""),
            ("20h", "Vozes Regionais", "SEGUNDA", ""),
            ("11h", "Barriguda Notícias", "TERÇA", ""),
            ("14h", "A leitura nossa de cada dia", "TERÇA", ""),
            ("15h", "Salve Maria", "TERÇA", ""),
            ("08h", "Capoeira em Foco", "QUARTA", ""),
            ("11h", "Barriguda Notícias", "QUARTA", ""),
            ("08h", "Sessão da Câmara", "QUINTA", ""),
            ("11h", "Barriguda Notícias", "QUINTA", ""),
            ("16h", "A voz da caatinga", "QUINTA", ""),
            ("17h", "Poder da Oração", "QUINTA", ""),
            ("09h", "Helicóptero Musical", "SEXTA", ""),
            ("10h", "Humor, Cordel e Paródia", "SEXTA", ""),
            ("11h", "Barriguda Notícias", "SEXTA", ""),
            ("13h", "Ao som do berimbau", "SEXTA", ""),
            ("14h", "Papo Contemporaneo", "SEXTA", ""),
            ("15h", "PodTeen", "SEXTA", ""),
            ("10h", "Re-Conexão Mental", "SÁBADO/ DIAS EXCLUSIVOS", ""),
            ("19h30m", "Barriguda Games", "SÁBADO/ DIAS EXCLUSIVOS", ""),
            ("10h", "Alimentação Escolar", "QUINTA", "MENSAL"),
            ("16h", "A arte de se conectar", "QUINTA", "MENSAL"),
            ("18h", "Mulheres Inspiradoras", "SEXTA", "MENSAL"),
            ("?h", "Conexão Sustentável", "SÁBADO/ DIAS EXCLUSIVOS", "MENSAL"),
            ("?h", "Poder e Saber", "SÁBADO/ DIAS EXCLUSIVOS", "MENSAL"),
            ("?h", "Visão Espírita", "SÁBADO/ DIAS EXCLUSIVOS", "MENSAL"),
            ("?h", "Euclebia Pereira", "SÁBADO/ DIAS EXCLUSIVOS", "MENSAL"),
            ("?h", "Vã Filosófia", "SÁBADO/ DIAS EXCLUSIVOS", "MENSAL"),
            ("16h", "CME Acontece", "QUINTA", "TRIMESTRAL"),
            ("15h", "Gaiola Vazia", "QUARTA", "QUIZENAL"),
            ("?h", "Direito de Saber", "QUINTA", "QUIZENAL"),
            ("?h", "Ivan Mendes", "SÁBADO/ DIAS EXCLUSIVOS", "SEMANAL"),
            ("?h", "Vozes do Quilombro", "SÁBADO/ DIAS EXCLUSIVOS", "SEMANAL"),
            ("?h", "Gabriela Explica!", "SÁBADO/ DIAS EXCLUSIVOS", "SEMANAL")
        ]

    # Limpar tabela antes de popular (opcional, para testes)
    cursor.execute("DELETE FROM programas")
    
    cursor.executemany(
        "INSERT INTO programas (horario, nome, dias, categoria) VALUES (?, ?, ?, ?)",
        dados_programas
    )
    
    db.commit()
    print(f"Sucesso: {len(dados_programas)} programas inseridos no SQLite.")

if __name__ == "__main__":
    popular_banco()