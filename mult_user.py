import flet as ft
import sqlite3
import hashlib

# Função para criptografar a senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Inicializa o banco de dados
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    
    # Criar tabela de usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)
    
    # Criar tabela de tarefas com compartilhamento
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        shared_with TEXT DEFAULT NULL,
        title TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        value REAL DEFAULT 0.0,
        completed INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()

# Função para cadastrar um novo usuário
def register_user(username, password):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    hashed_pass = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pass))
        conn.commit()
        ms = ft.mensa
    except sqlite3.IntegrityError:
        return False  # Usuário já existe
    finally:
        conn.close()
    return True

# Função de login
def login_user(username, password):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    hashed_pass = hash_password(password)
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_pass))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None

# Carregar tarefas do usuário e compartilhadas
def load_tasks(user_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM tasks WHERE user_id = ? OR shared_with = (SELECT username FROM users WHERE id = ?)
    """, (user_id, user_id))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

# Interface do app
def main(page: ft.Page):
    page.title = "Gerenciador de Tarefas Compartilhadas"
    page.scroll = "auto"
    
    # Inicializa banco
    init_db()
    
    task_list = ft.Column()
    
    # Campos de login e cadastro
    username_input = ft.TextField(label="Usuário")
    password_input = ft.TextField(label="Senha", password=True)
    login_button = ft.ElevatedButton("Entrar", on_click=lambda e: login())
    register_button = ft.ElevatedButton("Registrar", on_click=lambda e: register())
    
    # Inputs de tarefa
    title_input = ft.TextField(label="Tarefa")
    description_input = ft.TextField(label="Descrição")
    date_input = ft.TextField(label="Data (YYYY-MM-DD)")
    value_input = ft.TextField(label="Valor (R$)")
    share_input = ft.TextField(label="Compartilhar com (Usuário)")
    
    # Soma total
    total_label = ft.Text("Total: R$ 0.00", size=18, weight="bold")
    
    user_id = None  # Armazena o usuário logado

    # Atualizar tarefas
    def refresh_tasks():
        if user_id is None:
            return
        
        task_list.controls.clear()
        tasks = load_tasks(user_id)
        total_value = 0.0
        
        for task in tasks:
            task_id, owner, shared_with, title, desc, date, value, completed = task
            total_value += value
            
            # Checkbox de status
            checkbox = ft.Checkbox(label=f"{title} - R$ {value:.2f} ({'Compartilhada' if shared_with else 'Pessoal'})", 
                                   value=bool(completed))
            
            def toggle_status(e, task_id=task_id):
                conn = sqlite3.connect("tasks.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (int(e.control.value), task_id))
                conn.commit()
                conn.close()
                refresh_tasks()
            
            checkbox.on_change = toggle_status
            
            # Botão de excluir
            def delete_task(e, task_id=task_id):
                conn = sqlite3.connect("tasks.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                conn.close()
                refresh_tasks()
            
            delete_button = ft.IconButton(ft.icons.DELETE, on_click=delete_task, icon_color="red")
            
            task_list.controls.append(ft.Row([checkbox, delete_button]))
        
        total_label.value = f"Total: R$ {total_value:.2f}"
        page.update()

    # Adicionar nova tarefa
    def add_task(e):
        if user_id is None:
            return

        title = title_input.value
        desc = description_input.value
        date = date_input.value
        try:
            value = float(value_input.value)
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Valor inválido!"))
            page.snack_bar.open = True
            page.update()
            return

        if not title or not date:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            page.snack_bar.open = True
            page.update()
            return

        # Compartilhar com outro usuário (se existir)
        shared_with = share_input.value.strip()
        conn = sqlite3.connect("tasks.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (user_id, shared_with, title, description, date, value, completed) VALUES (?, ?, ?, ?, ?, ?, 0)", 
                       (user_id, shared_with if shared_with else None, title, desc, date, value))
        conn.commit()
        conn.close()
        
        title_input.value = ""
        description_input.value = ""
        date_input.value = ""
        value_input.value = ""
        share_input.value = ""
        
        refresh_tasks()

    # Login do usuário
    def login():
        nonlocal user_id
        username = username_input.value.strip()
        password = password_input.value.strip()
        
        user_id = login_user(username, password)
        if not user_id:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário ou senha incorretos!"))
            page.snack_bar.open = True
            page.update()
            return
        
        page.clean()
        page.add(ft.Text(f"Bem-vindo, {username}!", size=20, weight="bold"))
        page.add(ft.Column([title_input, description_input, date_input, value_input, share_input,
                            ft.ElevatedButton("Adicionar Tarefa", on_click=add_task), total_label, task_list]))
        refresh_tasks()

    # Registro do usuário
    def register():
        username = username_input.value.strip()
        password = password_input.value.strip()
        if not username or not password:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha usuário e senha!"))
            page.snack_bar.open = True
            page.update()
            return
        
        if register_user(username, password):
            page.snack_bar = ft.SnackBar(ft.Text("Usuário registrado com sucesso!"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário já existe!"))
        
        page.snack_bar.open = True
        page.update()

    # Tela de login inicial
    page.add(ft.Column([username_input, password_input, login_button, register_button]))

# Rodar app
ft.app(target=main) 