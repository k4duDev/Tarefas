#   Passo 3: Criar a tela principal

import flet as ft
import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect("tarefas.db", check_same_thread=False)
cursor = conn.cursor()

# Criar tabela de tarefas se não existir
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

# Função para carregar tarefas do usuário
def carregar_tarefas(usuario_id):
    cursor.execute("SELECT id, data, descricao, valor, status FROM tarefas WHERE usuario_id = ?", (usuario_id,))
    return cursor.fetchall()

# Função para adicionar tarefa
def adicionar_tarefa(usuario_id, empresa_id, data, descricao, valor):
    cursor.execute("INSERT INTO tarefas (usuario_id, empresa_id, data, descricao, valor, status) VALUES (?, ?, ?, ?, ?, 'Pendente')",
                   (usuario_id, empresa_id, data, descricao, valor))
    conn.commit()

# Função para atualizar tarefa
def atualizar_tarefa(tarefa_id, descricao, data, valor, status):
    cursor.execute("UPDATE tarefas SET descricao = ?, data = ?, valor = ?, status = ? WHERE id = ?",
                   (descricao, data, valor, status, tarefa_id))
    conn.commit()

# Função para excluir tarefa
def excluir_tarefa(tarefa_id):
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    conn.commit()

# Tela principal no Flet
def carregar_tela_principal(page: ft.Page):
    usuario_id = page.session.get("usuario_id")
    empresa_id = page.session.get("empresa_id")

    if not usuario_id:
        page.clean()
        page.add(ft.Text("Usuário não autenticado. Faça login."))
        return

    page.title = "Tarefas - Gerenciador"
    lista_tarefas = ft.Column()
    
    def atualizar_lista():
        lista_tarefas.controls.clear()
        tarefas = carregar_tarefas(usuario_id)
        for t in tarefas:
            lista_tarefas.controls.append(
                ft.Row([
                    ft.Text(t[1]),  # Data
                    ft.Text(t[2]),  # Descrição
                    ft.Text(f"R$ {t[3]:.2f}"),  # Valor
                    ft.Text(t[4]),  # Status
                    ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, t=t: editar_tarefa(page, t)),
                    ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, t=t: excluir_tarefa_e_atualizar(page, t[0]))
                ])
            )
        page.update()

    def adicionar_tarefa_click(e):
        adicionar_tarefa(usuario_id, empresa_id, data.value, descricao.value, float(valor.value))
        data.value = descricao.value = valor.value = ""
        atualizar_lista()

    def excluir_tarefa_e_atualizar(page, tarefa_id):
        excluir_tarefa(tarefa_id)
        atualizar_lista()

    def editar_tarefa(page, tarefa):
        def salvar_edicao(e):
            atualizar_tarefa(tarefa[0], desc_field.value, data_field.value, float(valor_field.value), status_field.value)
            page.dialog.open = False
            atualizar_lista()

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

    btn_adicionar = ft.ElevatedButton("Adicionar Tarefa", on_click=adicionar_tarefa_click)

    page.clean()
    page.add(ft.Text("Lista de Tarefas"), data, descricao, valor, btn_adicionar, lista_tarefas)
    atualizar_lista()

ft.app(target=carregar_tela_principal)
