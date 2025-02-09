#      Passo 4: Filtragem e soma dos valores


import flet as ft
import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect("tarefas.db", check_same_thread=False)
cursor = conn.cursor()

# Função para carregar tarefas do usuário com filtro
def carregar_tarefas(usuario_id, filtro="Todas"):
    if filtro == "Todas":
        cursor.execute("SELECT id, data, descricao, valor, status FROM tarefas WHERE usuario_id = ?", (usuario_id,))
    else:
        cursor.execute("SELECT id, data, descricao, valor, status FROM tarefas WHERE usuario_id = ? AND status = ?", 
                       (usuario_id, filtro))
    return cursor.fetchall()

# Função para calcular a soma total das tarefas
def calcular_soma(usuario_id, filtro="Todas"):
    if filtro == "Todas":
        cursor.execute("SELECT SUM(valor) FROM tarefas WHERE usuario_id = ?", (usuario_id,))
    else:
        cursor.execute("SELECT SUM(valor) FROM tarefas WHERE usuario_id = ? AND status = ?", (usuario_id, filtro))
    
    total = cursor.fetchone()[0]
    return total if total else 0

# Tela principal com filtro e soma de valores
def carregar_tela_principal(page: ft.Page):
    usuario_id = page.session.get("usuario_id")

    if not usuario_id:
        page.clean()
        page.add(ft.Text("Usuário não autenticado. Faça login."))
        return

    page.title = "Tarefas - Gerenciador"
    lista_tarefas = ft.Column()
    total_valor_text = ft.Text(f"Total: R$ 0.00", size=18, weight="bold")

    filtro_dropdown = ft.Dropdown(
        label="Filtrar por Status",
        options=[ft.dropdown.Option("Todas"), ft.dropdown.Option("Pendente"), ft.dropdown.Option("Concluído")],
        value="Todas"
    )

    def atualizar_lista(e=None):
        filtro = filtro_dropdown.value
        lista_tarefas.controls.clear()
        
        tarefas = carregar_tarefas(usuario_id, filtro)
        total_valor = calcular_soma(usuario_id, filtro)
        
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

        total_valor_text.value = f"Total: R$ {total_valor:.2f}"
        page.update()

    filtro_dropdown.on_change = atualizar_lista

    def adicionar_tarefa_click(e):
        adicionar_tarefa(usuario_id, data.value, descricao.value, float(valor.value))
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
    page.add(
        ft.Text("Lista de Tarefas"),
        filtro_dropdown,
        lista_tarefas,
        total_valor_text,
        ft.Row([data, descricao, valor, btn_adicionar])
    )
    atualizar_lista()

ft.app(target=carregar_tela_principal)
