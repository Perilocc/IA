PROMPT_TRIAGEM = f"""
    Analise os processos jurídicos abaixo e retorne APENAS um JSON válido.

    O retorno deve ser uma LISTA de objetos JSON, contendo para cada processo as seguintes chaves:

    - "processo": número do processo
    - "categoria": classifique em uma categoria jurídica apropriada
    (ex: Previdenciário, Cível, Trabalhista, Tributário, Administrativo)

    - "prioridade": número de 1 a 5
    Onde:
    1 = baixa prioridade
    2 = prioridade moderada
    3 = prioridade média
    4 = prioridade alta
    5 = prioridade crítica

    - "complexidade": classifique como:
    "Baixa", "Média" ou "Alta"

    - "risco_financeiro": classifique como:
    "Baixo", "Médio" ou "Alto"

    - "resposta_rascunho":
    escreva um pequeno resumo jurídico profissional com possível próximo passo processual.

    Considere:
    - assunto do processo
    - valor da causa
    - status processual
    - quantidade de partes
    - presença de perícia
    - tipo da ação

    Retorne SOMENTE JSON válido.
    Não use markdown.
    Não explique nada fora do JSON.

    Processos:
"""