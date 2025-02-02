import sqlite3


# Conectar ao banco de dados
class Tarefas():

    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()

# Criar tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        concluida INTEGER DEFAULT 0
        )
        """)
    conn.commit()
    conn.close()