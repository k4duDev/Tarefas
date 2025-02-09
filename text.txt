import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from banco import Tarefas

# Funções CRUD
def carregar_tarefas():
    tree.delete(*tree.get_children())
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas")
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
    conn.close()

def adicionar_tarefa():

titulo = entry_titulo.get()
descricao = entry_descricao.get()

if titulo:
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tarefas (titulo, descricao) VALUES (?, ?)", (titulo, descricao))
    conn.commit()
    conn.close()
    carregar_tarefas()
    entry_titulo.delete(0, tk.END)
    entry_descricao.delete(0, tk.END)
else:
    messagebox.showwarning("Aviso", "O título não pode estar vazio!")

def excluir_tarefa():
selecionado = tree.selection()
    if selecionado:
        id_tarefa = tree.item(selecionado)['values'][0]
        conn = sqlite3.connect("agenda.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tarefas WHERE id=?", (id_tarefa,))
        conn.commit()
        conn.close()
        carregar_tarefas()
else:
    messagebox.showwarning("Aviso", "Selecione uma tarefa para excluir!")

def editar_tarefa():
selecionado = tree.selection()
if selecionado:
    id_tarefa = tree.item(selecionado)['values'][0]
    novo_titulo = entry_titulo.get()
    nova_descricao = entry_descricao.get()

    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET titulo=?, descricao=? WHERE id=?", (novo_titulo, nova_descricao, id_tarefa))
    conn.commit()
    conn.close()
    carregar_tarefas()
    else:
    messagebox.showwarning("Aviso", "Selecione uma tarefa para editar!")

# Criar janela principal
root = tk.Tk()
root.title("Agenda de Tarefas")
root.geometry("500x400")

# Campos de entrada
tk.Label(root, text="Título:").pack()
entry_titulo = tk.Entry(root, width=50)
entry_titulo.pack()

tk.Label(root, text="Descrição:").pack()
entry_descricao = tk.Entry(root, width=50)
entry_descricao.pack()

# Botões
frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=10)

btn_adicionar = tk.Button(frame_botoes, text="Adicionar", command=adicionar_tarefa)
btn_adicionar.grid(row=0, column=0, padx=5)

btn_editar = tk.Button(frame_botoes, text="Editar", command=editar_tarefa)
btn_editar.grid(row=0, column=1, padx=5)

btn_excluir = tk.Button(frame_botoes, text="Excluir", command=excluir_tarefa)
btn_excluir.grid(row=0, column=2, padx=5)

# Tabela de Tarefas
columns = ("ID", "Título", "Descrição", "Concluída")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("ID", text="ID")
tree.heading("Título", text="Título")
tree.heading("Descrição", text="Descrição")
tree.heading("Concluída", text="Concluída")
tree.pack(fill="both", expand=True)

# Carregar tarefas ao iniciar
carregar_tarefas()

# Executar aplicação
root.mainloop()