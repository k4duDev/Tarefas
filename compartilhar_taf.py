#     Passo 5: Compartilhamento de Tarefas


# Função para carregar tarefas da empresa do usuário logado
def carregar_tarefas_empresa(empresa_id, filtro="Todas"):
    if filtro == "Todas":
        cursor.execute("SELECT id, data, descricao, valor, status FROM tarefas WHERE empresa_id = ?", (empresa_id,))
    else:
        cursor.execute("SELECT id, data, descricao, valor, status FROM tarefas WHERE empresa_id = ? AND status = ?", 
                       (empresa_id, filtro))
    return cursor.fetchall()
