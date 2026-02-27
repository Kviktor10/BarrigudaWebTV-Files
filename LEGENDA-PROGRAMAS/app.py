#!/usr/bin/env python3
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_FILE = 'barriguda_tv.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS programas 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      titulo TEXT, subtitulo TEXT, estado TEXT, 
                      ativo INTEGER DEFAULT 0,
                      visivel INTEGER DEFAULT 1)''')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM programas")
        if cursor.fetchone()[0] == 0:
            conn.execute("INSERT INTO programas (titulo, subtitulo, estado, ativo, visivel) VALUES (?, ?, ?, 1, 1)",
                         ('BARRIGUDA WEB TV', 'Irecê - Bahia', 'ONLINE'))
        conn.commit()

@app.route('/')
def painel():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        lista = conn.execute("SELECT * FROM programas ORDER BY id DESC").fetchall()
        status_visivel = conn.execute("SELECT visivel FROM programas WHERE ativo = 1").fetchone()
        visivel = status_visivel['visivel'] if status_visivel else 0
    return render_template('painel.html', programas=lista, visivel=visivel)

@app.route('/get_active')
def get_active():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        active = conn.execute("SELECT * FROM programas WHERE ativo = 1").fetchone()
    if active:
        return jsonify(dict(active))
    return jsonify({"visivel": 0, "titulo": "", "subtitulo": "", "estado": ""})

# --- NOVAS ROTAS PARA EDIÇÃO ---
@app.route('/get_programa/<int:id>')
def get_programa(id):
    """Busca os dados de um programa para preencher o formulário de edição"""
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        p = conn.execute("SELECT * FROM programas WHERE id = ?", (id,)).fetchone()
    return jsonify(dict(p))

@app.route('/editar', methods=['POST'])
def editar():
    """Salva as alterações de um programa existente"""
    id = request.form.get('id')
    titulo = request.form.get('titulo')
    subtitulo = request.form.get('subtitulo')
    estado = request.form.get('estado')
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE programas SET titulo=?, subtitulo=?, estado=? WHERE id=?", 
                     (titulo, subtitulo, estado, id))
    return "Atualizado", 200
# -------------------------------

@app.route('/add', methods=['POST'])
def add():
    titulo = request.form.get('titulo')
    subtitulo = request.form.get('subtitulo')
    estado = request.form.get('estado')
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO programas (titulo, subtitulo, estado, ativo, visivel) VALUES (?, ?, ?, 0, 1)",
                     (titulo, subtitulo, estado))
    return "Salvo", 200

@app.route('/selecionar/<int:id>', methods=['POST'])
def selecionar(id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE programas SET ativo = 0")
        conn.execute("UPDATE programas SET ativo = 1 WHERE id = ?", (id,))
    return "Ativado", 200

@app.route('/toggle_visibilidade', methods=['POST'])
def toggle_visibilidade():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE programas SET visivel = 1 - visivel WHERE ativo = 1")
    return "OK", 200

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM programas WHERE id = ?", (id,))
    return "Deletado", 200

@app.route('/overlay')
def overlay():
    return render_template('overlay.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
