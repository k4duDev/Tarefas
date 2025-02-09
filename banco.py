#      Passo 1: Banco de dados(Usuários, Empresa)

import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect("tarefas.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabelas se não existirem
cursor.execute("""
CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT, email TEXT UNIQUE, senha TEXT, empresa_id INTEGER,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id)
)
""")

conn.commit()

# Função para registrar usuário
def registrar_usuario(nome, email, senha, empresa):
    # Verificar se a empresa já existe
    cursor.execute("SELECT id FROM empresas WHERE nome = ?", (empresa,))
    empresa_row = cursor.fetchone()

    if empresa_row:
        empresa_id = empresa_row[0]
    else:
        cursor.execute("INSERT INTO empresas (nome) VALUES (?)", (empresa,))
        empresa_id = cursor.lastrowid
        conn.commit()

    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha, empresa_id) VALUES (?, ?, ?, ?)",
                       (nome, email, senha, empresa_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Usuário já existe

# Função para autenticar login
def autenticar_usuario(email, senha):
    cursor.execute("SELECT id, nome, empresa_id FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    return cursor.fetchone()
