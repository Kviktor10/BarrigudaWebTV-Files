import sqlite3

# Conecta ao banco existente
conn = sqlite3.connect('barriguda_tv.db')
cursor = conn.cursor()

try:
    # Tenta adicionar a coluna que está faltando
    cursor.execute("ALTER TABLE programas ADD COLUMN visivel INTEGER DEFAULT 1")
    conn.commit()
    print("Sucesso! Coluna 'visivel' adicionada.")
except sqlite3.OperationalError as e:
    print(f"Aviso: {e}")

conn.close()