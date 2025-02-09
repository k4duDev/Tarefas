#     Passo 2 :Interface de Login e Reistro no flet

import flet as ft

def main(page: ft.Page):
    page.title = "Login - Gerenciador de Tarefas"
    
    email = ft.TextField(label="Email")
    senha = ft.TextField(label="Senha", password=True)
    nome = ft.TextField(label="Nome")
    empresa = ft.TextField(label="Empresa")
    
    login_status = ft.Text("")
    
    def realizar_login(e):
        usuario = autenticar_usuario(email.value, senha.value)
        if usuario:
            page.session.set("usuario_id", usuario[0])
            page.session.set("empresa_id", usuario[2])
            login_status.value = "Login bem-sucedido!"
            page.update()
            carregar_tela_principal(page)
        else:
            login_status.value = "Email ou senha inválidos"
            page.update()

    def realizar_registro(e):
        if registrar_usuario(nome.value, email.value, senha.value, empresa.value):
            login_status.value = "Registro bem-sucedido! Faça login."
        else:
            login_status.value = "Erro: Email já cadastrado."
        page.update()
    
    btn_login = ft.ElevatedButton("Login", on_click=realizar_login)
    btn_registro = ft.ElevatedButton("Registrar", on_click=realizar_registro)

    page.add(ft.Text("Login"), email, senha, btn_login, 
             ft.Text("Registrar"), nome, empresa, senha, btn_registro, login_status)

ft.app(target=main)