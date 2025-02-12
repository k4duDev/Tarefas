import flet as ft
import sqlite3

conn = sqlite3.connect("tarefas.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabelas
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
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
    )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER, empresa_id INTEGER,
    data TEXT, descricao TEXT, valor REAL, status TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (empresa_id) REFERENCES empresas(id)
    )
""")

conn.commit()



conn = sqlite3.connect("tarefas.db", check_same_thread=False)
cursor = conn.cursor()

def verificar_login(email, senha):
    cursor.execute("SELECT id, empresa_id FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
    return cursor.fetchone()

def cadastrar_usuario(nome, email, senha, empresa):
    cursor.execute("INSERT OR IGNORE INTO empresas (nome) VALUES (?)", (empresa,))
    cursor.execute("SELECT id FROM empresas WHERE nome = ?", (empresa,))
    empresa_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO usuarios (nome, email, senha, empresa_id) VALUES (?, ?, ?, ?)", 
                   (nome, email, senha, empresa_id))
    conn.commit()
    return verificar_login(email, senha)

def carregar_tela_login(page: ft.Page):
    page.title = "Login"

    email = ft.TextField(label="Email")
    senha = ft.TextField(label="Senha", password=True)
    msg_erro = ft.Text("", color="red")

    def entrar_click(e):
        user = verificar_login(email.value, senha.value)
        if user:
            page.session.set("usuario_id", user[0])
            page.session.set("empresa_id", user[1])
            carregar_tela_tarefas(page)
        else:
            msg_erro.value = "Credenciais inválidas!"
            page.update()

    btn_login = ft.ElevatedButton("Entrar", on_click=entrar_click)

    nome = ft.TextField(label="Nome")
    empresa = ft.TextField(label="Nome da Empresa")
    btn_cadastrar = ft.ElevatedButton("Cadastrar", on_click=lambda e: cadastrar_usuario(nome.value, email.value, senha.value, empresa.value))

    page.clean()
    page.add(ft.Text("Login"), email, senha, btn_login, msg_erro, ft.Text("Cadastro"), nome, empresa, btn_cadastrar)

ft.app(target=carregar_tela_login)

# ----------------------------------------------------------------

def carregar_tela_tarefas(page: ft.Page):
    usuario_id = page.session.get("usuario_id")
    empresa_id = page.session.get("empresa_id")

    if not usuario_id:
        page.clean()
        page.add(ft.Text("Usuário não autenticado. Faça login."))
        return

    lista_tarefas = ft.Column()
    total_valor_text = ft.Text(f"Total: R$ 0.00", size=18, weight="bold")

    filtro_dropdown = ft.Dropdown(
        label="Filtrar por Status",
        options=[ft.dropdown.Option("Todas"), ft.dropdown.Option("Pendente"), ft.dropdown.Option("Concluído")],
        value="Todas"
    )

    def carregar_tarefas():
        lista_tarefas.controls.clear()
        cursor.execute("SELECT id, data, descricao, valor, status FROM tarefas WHERE empresa_id = ?", (empresa_id,))
        tarefas = cursor.fetchall()

        total_valor = sum(t[3] for t in tarefas)
        total_valor_text.value = f"Total: R$ {total_valor:.2f}"

        for t in tarefas:
            lista_tarefas.controls.append(
                ft.Row([
                    ft.Text(t[1]), ft.Text(t[2]), ft.Text(f"R$ {t[3]:.2f}"), ft.Text(t[4]),
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, t=t: editar_tarefa(page, t)),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, t=t: excluir_tarefa(page, t[0]))
                ])
            )
        page.update()

    def adicionar_tarefa(e):
        cursor.execute("INSERT INTO tarefas (usuario_id, empresa_id, data, descricao, valor, status) VALUES (?, ?, ?, ?, ?, ?)", 
                       (usuario_id, empresa_id, data.value, descricao.value, float(valor.value), "Pendente"))
        conn.commit()
        carregar_tarefas()

    def excluir_tarefa(page, tarefa_id):
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        carregar_tarefas()

    def editar_tarefa(page, tarefa):
        def salvar_edicao(e):
            cursor.execute("UPDATE tarefas SET descricao=?, data=?, valor=?, status=? WHERE id=?", 
                           (desc_field.value, data_field.value, float(valor_field.value), status_field.value, tarefa[0]))
            conn.commit()
            page.dialog.open = False
            carregar_tarefas()

        data_field = ft.TextField(label="Data", value=tarefa[1])
        desc_field = ft.TextField(label="Descrição", value=tarefa[2])
        valor_field = ft.TextField(label="Valor", value=str(tarefa[3]))
        status_field = ft.Dropdown(label="Status", options=[ft.dropdown.Option("Pendente"), ft.dropdown.Option("Concluído")], value=tarefa[4])

        page.dialog = ft.AlertDialog(
            title=ft.Text("Editar Tarefa"),
            content=ft.Column([data_field, desc_field, valor_field, status_field]),
            actions=[ft.ElevatedButton("Salvar", on_click=salvar_edicao)]
        )
        page.dialog.open = True
        page.update()

    data = ft.TextField(label="Data")
    descricao = ft.TextField(label="Descrição")
    valor = ft.TextField(label="Valor")

    btn_adicionar = ft.ElevatedButton("Adicionar Tarefa", on_click=adicionar_tarefa)

    page.clean()
    page.add(ft.Text("Tarefas"), filtro_dropdown, lista_tarefas, total_valor_text, ft.Row([data, descricao, valor, btn_adicionar]))
    carregar_tarefas()

ft.app(target=carregar_tela_tarefas)