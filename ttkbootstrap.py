import sqlite3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# Criar banco de dados e tabela
conn = sqlite3.connect("agenda.db")
cursor = conn.cursor()
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

# Funções CRUD
def carregar_tarefas():
    tree.delete(*tree.get_children())
    conn = sqlite3.connect("agenda.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tarefas")
    for row in cursor.fetchall():
        status = "✔️" if row[3] else "❌"
        tree.insert("", "end", values=(row[0], row[1], row[2], status))
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
        entry_titulo.delete(0, ttk.END)
        entry_descricao.delete(0, ttk.END)
    else:
        ttk.messagebox.showwarning("Aviso", "O título não pode estar vazio!")

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
        ttk.messagebox.showwarning("Aviso", "Selecione uma tarefa para excluir!")

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
        ttk.messagebox.showwarning("Aviso", "Selecione uma tarefa para editar!")

def concluir_tarefa():
    selecionado = tree.selection()
    if selecionado:
        id_tarefa = tree.item(selecionado)['values'][0]
        conn = sqlite3.connect("agenda.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tarefas SET concluida=1 WHERE id=?", (id_tarefa,))
        conn.commit()
        conn.close()
        carregar_tarefas()
    else:
        ttk.messagebox.showwarning("Aviso", "Selecione uma tarefa para concluir!")

# Criar janela principal com ttkbootstrap
root = ttk.Window(themename="darkly")  # Temas: "cosmo", "darkly", "superhero", "flatly" etc.
root.title("Agenda de Tarefas")
root.geometry("600x450")

# Campos de entrada
frame_inputs = ttk.Frame(root)
frame_inputs.pack(pady=10)

ttk.Label(frame_inputs, text="Título:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
entry_titulo = ttk.Entry(frame_inputs, width=40)
entry_titulo.grid(row=0, column=1, padx=5)

ttk.Label(frame_inputs, text="Descrição:", font=("Arial", 12)).grid(row=1, column=0, padx=5)
entry_descricao = ttk.Entry(frame_inputs, width=40)
entry_descricao.grid(row=1, column=1, padx=5)

# Botões estilizados
frame_botoes = ttk.Frame(root)
frame_botoes.pack(pady=10)

btn_adicionar = ttk.Button(frame_botoes, text="Adicionar", bootstyle=SUCCESS, command=adicionar_tarefa)
btn_adicionar.grid(row=0, column=0, padx=5)

btn_editar = ttk.Button(frame_botoes, text="Editar", bootstyle=INFO, command=editar_tarefa)
btn_editar.grid(row=0, column=1, padx=5)

btn_concluir = ttk.Button(frame_botoes, text="Concluir", bootstyle=WARNING, command=concluir_tarefa)
btn_concluir.grid(row=0, column=2, padx=5)

btn_excluir = ttk.Button(frame_botoes, text="Excluir", bootstyle=DANGER, command=excluir_tarefa)
btn_excluir.grid(row=0, column=3, padx=5)

# Tabela de Tarefas
columns = ("ID", "Título", "Descrição", "Status")
tree = ttk.Treeview(root, columns=columns, show="headings", bootstyle="primary")
tree.heading("ID", text="ID")
tree.heading("Título", text="Título")
tree.heading("Descrição", text="Descrição")
tree.heading("Status", text="Status")
tree.column("ID", width=30)
tree.column("Título", width=200)
tree.column("Descrição", width=250)
tree.column("Status", width=60)
tree.pack(fill="both", expand=True, padx=10, pady=10)

# Carregar tarefas ao iniciar
carregar_tarefas()

# Executar aplicação
root.mainloop()