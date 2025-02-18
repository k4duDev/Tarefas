import flet as ft
import sqlite3

def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company TEXT,
                        username TEXT UNIQUE,
                        name TEXT,
                        email TEXT,
                        password TEXT,
                        admin INTEGER DEFAULT 0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        company TEXT,
                        date TEXT,
                        description TEXT,
                        value REAL,
                        status TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def register_user(company, username, name, email, password, admin=0):
    if not all([company, username, name, email, password]):
        return False, "Todos os campos são obrigatórios!"
    
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (company, username, name, email, password, admin) VALUES (?, ?, ?, ?, ?, ?)",
                       (company, username, name, email, password, admin))
        conn.commit()
        conn.close()
        return True, "Cadastro realizado com sucesso!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Usuário já existe!"

def add_task(user_id, company, date, description, value, status):
    if not all([date, description, value, status]):
        return False, "Todos os campos são obrigatórios!"
    
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (user_id, company, date, description, value, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, company, date, description, value, status))
    conn.commit()
    conn.close()
    return True, "Tarefa adicionada!"

def get_user(username, password):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, company, admin FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def get_tasks(user_id, company, is_admin):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("SELECT date, description, value, status FROM tasks WHERE company = ?", (company,))
    else:
        cursor.execute("SELECT date, description, value, status FROM tasks WHERE user_id = ?", (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def sum_tasks(user_id, company, is_admin):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    if is_admin:
        cursor.execute("SELECT SUM(value) FROM tasks WHERE company = ?", (company,))
    else:
        cursor.execute("SELECT SUM(value) FROM tasks WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0] or 0
    conn.close()
    return total

def main(page: ft.Page):
    page.title = "Task Manager"
    page.window_width = 900
    page.window_height = 600
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    
    def login_click(e):
        if not usuario.value or not senha.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos!"))
            page.snack_bar.open = True
            page.update()
            return
        
        user = get_user(usuario.value, senha.value)
        if user:
            page.session.set("user_id", user[0])
            page.session.set("company", user[1])
            page.session.set("is_admin", user[2])
            page.snack_bar = ft.SnackBar(ft.Text("Login realizado!"))
            page.snack_bar.open = True
            page.update()
            page.clean()
            task_screen()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Usuário ou senha incorretos!"))
            page.snack_bar.open = True
            page.update()
    
    def cadastro_click(e):
        page.clean()
        cadastro_tela()
    
    def voltar_login(e):
        page.clean()
        login_tela()
    
    def task_screen():
        page.window_width = 900
        page.window_height = 600
        user_id = page.session.get("user_id")
        company = page.session.get("company")
        is_admin = page.session.get("is_admin")
        
        tasks = get_tasks(user_id, company, is_admin)
        total = sum_tasks(user_id, company, is_admin)
        task_list = ft.Column([ft.Text(f"{t[0]} - {t[1]} - R${t[2]} - {t[3]}") for t in tasks])
        
        page.add(ft.Text("Tarefas da Empresa", size=24, weight=ft.FontWeight.BOLD),
                 task_list,
                 ft.Text(f"Total: R${total:.2f}", size=20, weight=ft.FontWeight.BOLD))
    
    def login_tela():
        page.window_width = 400
        page.window_height = 300
        global usuario, senha
        usuario = ft.TextField(label="Usuário", icon=ft.icons.PERSON)
        senha = ft.TextField(label="Senha", password=True, can_reveal_password=True, icon=ft.icons.LOCK)
        botao_login = ft.ElevatedButton("Login", icon=ft.icons.LOGIN, on_click=login_click)
        botao_cadastro = ft.TextButton("Cadastre-se", icon=ft.icons.PERSON_ADD, on_click=cadastro_click)
        
        page.add(
            ft.Column([
                ft.Text("Bem-vindo!", size=24, weight=ft.FontWeight.BOLD),
                usuario,
                senha,
                botao_login,
                botao_cadastro
            ])
        )
    
    login_tela()

init_db()
ft.app(target=main)
