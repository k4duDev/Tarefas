#   Passo 6: Tela Principal com Compartilhamento


def carregar_tela_principal(page: ft.Page):
    usuario_id = page.session.get("usuario_id")
    empresa_id = page.session.get("empresa_id")

    if not usuario_id:
        page.clean()
        page.add(ft.Text("Usuário não autenticado. Faça login."))
        return

    page.title = "Tarefas - Compartilhadas"
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
        
        tarefas = carregar_tarefas_empresa(empresa_id, filtro)
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
        adicionar_tarefa(usuario_id, empresa_id, data.value, descricao.value, float(valor.value))
        data.value = descricao.value = valor.value = ""
        atualizar_lista()

    data = ft.TextField(label="Data")
    descricao = ft.TextField(label="Descrição")
    valor = ft.TextField(label="Valor")

    btn_adicionar = ft.ElevatedButton("Adicionar Tarefa", on_click=adicionar_tarefa_click)

    page.clean()
    page.add(
        ft.Text("Lista de Tarefas Compartilhadas"),
        filtro_dropdown,
        lista_tarefas,
        total_valor_text,
        ft.Row([data, descricao, valor, btn_adicionar])
    )
    atualizar_lista()

ft.app(target=carregar_tela_principal)