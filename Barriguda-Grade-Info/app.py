from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__, static_folder='.')

# ==========================================
# PADRÃO SINGLETON: Conexão com o Banco
# ==========================================
class DatabaseConnection:
    _instance = None

    def __new__(cls, db_name='grade_radio.db'):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.db_name = db_name
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            # Tabela atualizada para suportar dias e categorias simultaneamente
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS programas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    horario TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    dias TEXT NOT NULL,
                    categoria TEXT
                )
            ''')
            conn.commit()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row # Retorna os dados como dicionários
        return conn

# ==========================================
# PADRÃO REPOSITORY: Lógica de CRUD isolada
# ==========================================
class ProgramaRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all(self):
        with self.db.get_connection() as conn:
            progs = conn.execute('SELECT * FROM programas').fetchall()
            return [dict(p) for p in progs]

    def insert(self, data):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO programas (horario, nome, dias, categoria) VALUES (?, ?, ?, ?)',
                (data['horario'], data['nome'], data['dias'], data.get('categoria', ''))
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, id_prog, data):
        with self.db.get_connection() as conn:
            conn.execute(
                'UPDATE programas SET horario=?, nome=?, dias=?, categoria=? WHERE id=?',
                (data['horario'], data['nome'], data['dias'], data.get('categoria', ''), id_prog)
            )
            conn.commit()

    def delete(self, id_prog):
        with self.db.get_connection() as conn:
            conn.execute('DELETE FROM programas WHERE id=?', (id_prog,))
            conn.commit()

# Instância do repositório
repo = ProgramaRepository()

# ==========================================
# ROTAS FLASK (Endpoints RESTful)
# ==========================================
@app.route('/')
def index():
    return render_template('admin.html')

@app.route('/grade.html')
def grade():
    return render_template('grade.html')

@app.route('/api/programas', methods=['GET'])
def listar():
    return jsonify(repo.get_all())

@app.route('/api/programas', methods=['POST'])
def criar():
    data = request.json
    new_id = repo.insert(data)
    return jsonify({'status': 'sucesso', 'id': new_id}), 201

@app.route('/api/programas/<int:id>', methods=['PUT'])
def atualizar(id):
    repo.update(id, request.json)
    return jsonify({'status': 'sucesso'})

@app.route('/api/programas/<int:id>', methods=['DELETE'])
def deletar(id):
    repo.delete(id)
    return jsonify({'status': 'sucesso'})

if __name__ == '__main__':
    # Roda o mini-servidor web na porta 5000
    app.run(debug=True, port=5000)