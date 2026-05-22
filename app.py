import streamlit as st
import requests
from datetime import datetime, date

# ------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------
st.set_page_config(
    page_title="Gestão Farmacêutica",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_URL = "http://127.0.0.1:8000"
AI_SERVICE_URL = "http://127.0.0.1:8001" # Serviço RAG rodando isolado

# ------------------------------
# ESTILOS E CSS CUSTOMIZADO
# ------------------------------
st.markdown(
    """
<style>
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] div[data-testid="stWidgetLabel"],
[data-testid="stSidebar"] div[role="radiogroup"],
[data-testid="stSidebar"] div[role="radiogroup"] > div {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background-color: transparent !important;
    width: 100% !important; 
    max-width: 100% !important;
    display: flex !important; 
    box-sizing: border-box !important; 
    padding: 12px 16px !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease, color 0.2s ease !important;
    border: 1px solid transparent !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label p {
    color: #e2e8f0 !important;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background-color: #1e293b !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
    background-color: #1d4ed8 !important;
    border: 1px solid #3b82f6 !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Cards de Métricas */
.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    border-color: #3b82f6;
}
.metric-card h2 {
    color: #38bdf8;
    font-size: 2.2rem;
    margin: 0;
    font-weight: 800;
}
.metric-card p {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
    font-weight: 500;
}

/* Títulos de Seção */
.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #f8fafc;
    border-bottom: 2px solid #3b82f6;
    padding-bottom: 8px;
    margin-top: 10px;
    margin-bottom: 20px;
}

/* Badges de Status */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.badge-ativo {
    background: #064e3b;
    color: #34d399;
    border: 1px solid #059669;
}
.badge-inativo {
    background: #7f1d1d;
    color: #fca5a5;
    border: 1px solid #dc2626;
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------
# HELPERS HTTP
# ------------------------------
def get(endpoint: str):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", timeout=8)
        return r.json() if r.ok else {}
    except Exception:
        return {}

def post(endpoint: str, data: dict):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=8)
        try:
            payload = r.json()
        except ValueError:
            payload = {"mensagem": "Operação realizada com sucesso"} if r.ok else {"detail": "Erro de processamento da API"}
        return r.ok, payload
    except Exception as exc:
        return False, {"detail": str(exc)}

def post_files(endpoint: str, files):
    try:
        r = requests.post(f"{AI_SERVICE_URL}{endpoint}", files=files, timeout=120)
        try:
            payload = r.json()
        except ValueError:
            payload = {"detail": "Erro de processamento do serviço de IA"}
        return r.ok, payload
    except Exception as exc:
        return False, {"detail": str(exc)}

# ------------------------------
# HELPERS UI
# ------------------------------
def badge_status_funcionario(status: str):
    if status.lower() == "ativo":
        return '<span class="status-badge badge-ativo">Ativo</span>'
    return f'<span class="status-badge badge-inativo">{status}</span>'

def linha_sep():
    st.markdown("---")

def render_chunk_sources(sources):
    if not sources:
        return

    with st.expander("📚 Trechos recuperados", expanded=False):
        for index, source in enumerate(sources, 1):
            source_id = source.get("id", "-")
            content = source.get("content", "")
            preview = content[:700] + ("..." if len(content) > 700 else "")

            st.markdown(f"**#{index} — {source_id}**")
            st.caption(f"{len(content)} caracteres recuperados")
            st.code(preview, language="text")
            if index < len(sources):
                st.divider()

# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: white;'>💊 FarmacoRAG</h2>", unsafe_allow_html=True)
st.sidebar.caption("<div style='text-align: center; color: #94a3b8;'>Painel de Gestão Farmacêutica</div>", unsafe_allow_html=True)
st.sidebar.divider()

pagina = st.sidebar.radio(
    "Módulos",
    [
        "📊 Dashboard",
        "📦 Estoque",
        "👥 Funcionários",
        "🏭 Fornecedores",
        "💰 Vendas",
        "📄 Documentos",
        "🤖 Assistente IA",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if st.sidebar.button("🔌 Testar conexão API", use_container_width=True):
    ping = get("/dashboard/")
    if ping:
        st.sidebar.success("API Online 🟢")
    else:
        st.sidebar.error("API Offline 🔴")

# ------------------------------
# DASHBOARD
# ------------------------------
if pagina == "📊 Dashboard":
    st.title("📊 Visão Geral da Farmácia")
    dados = get("/dashboard/")
    fornecedores = get("/fornecedores/").get("fornecedores", [])

    if not dados:
        st.error("⚠️ Não foi possível conectar na API. Inicie o backend e tente novamente.")
        st.stop()

    st.markdown('<div class="section-title">Resumo Operacional</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><h2>{dados["medicamentos"]["total"]}</h2><p>Medicamentos Totais</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><h2>{dados["medicamentos"]["estoque_baixo"]}</h2><p>Estoque Baixo</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><h2>{dados["funcionarios"]["total"]}</h2><p>Funcionários Ativos</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><h2>{dados["vendas"]["total"]}</h2><p>Vendas Registradas</p></div>', unsafe_allow_html=True)

# ------------------------------
# MEDICAMENTOS
# ------------------------------
elif pagina == "📦 Estoque":
    st.title("📦 Gestão de Medicamentos")

    with st.expander("➕ Cadastrar Novo Medicamento", expanded=False):
        with st.form("form_medicamento"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome do Medicamento")
                categoria = st.text_input("Categoria")
                validade = st.date_input("Data de Validade", value=date.today())
            with c2:
                preco = st.number_input("Preço (R$)", min_value=0.01, step=0.5, value=10.0)
                estoque = st.number_input("Estoque Inicial", min_value=0, step=1, value=1)

            if st.form_submit_button("💾 Salvar Medicamento"):
                if not nome:
                    st.warning("Informe o nome do medicamento.")
                else:
                    ok, resp = post("/medicamentos/", {"nome": nome, "categoria": categoria, "preco": float(preco), "estoque": int(estoque), "validade": str(validade)})
                    st.success(resp.get("mensagem", "Medicamento cadastrado.")) if ok else st.error(resp.get("detail", "Erro ao cadastrar"))

    linha_sep()
    st.markdown('<div class="section-title">📦 Inventário de Medicamentos</div>', unsafe_allow_html=True)

    dados = get("/medicamentos/")
    lista = dados.get("medicamentos", [])
    apenas_estoque_baixo = st.toggle("🚨 Destacar apenas estoque baixo (< 10)")

    if apenas_estoque_baixo:
        lista = [m for m in lista if int(m.get("estoque", 0)) < 10]

    if lista:
        for med in lista:
            with st.container():
                c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 2, 2, 2, 2])
                c1.write(f"#{med['id']}")
                c2.write(f"**{med['nome']}**")
                c3.write(med.get("categoria") or "-")
                c4.write(f"R$ {float(med['preco']):.2f}")
                c5.write(f"📦 Est: {med['estoque']}")
                c6.write(f"📅 {med.get('validade', '-')}")
                st.divider()
    else:
        st.info("Nenhum medicamento encontrado para os critérios selecionados.")

# ------------------------------
# FUNCIONARIOS
# ------------------------------
elif pagina == "👥 Funcionários":
    st.title("👥 Gestão de Funcionários")

    aba1, aba2 = st.tabs(["📋 Lista de Funcionários", "➕ Cadastrar Novo"])

    with aba2:
        with st.form("form_funcionario"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome completo")
                cargo = st.text_input("Cargo")
            with c2:
                telefone = st.text_input("Telefone")
                status = st.selectbox("Status", ["Ativo", "Inativo", "Férias", "Afastado"])

            if st.form_submit_button("💾 Cadastrar Funcionário"):
                if not nome or not cargo:
                    st.warning("Preencha o nome e o cargo.")
                else:
                    ok, resp = post("/funcionarios/", {"nome": nome, "cargo": cargo, "telefone": telefone, "status": status})
                    st.success(resp.get("mensagem", "Funcionário cadastrado.")) if ok else st.error(resp.get("detail", "Erro no cadastro"))

    with aba1:
        dados = get("/funcionarios/")
        funcionarios = dados.get("funcionarios", [])

        if funcionarios:
            for f in funcionarios:
                c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 2])
                c1.write(f"#{f['id']}")
                c2.write(f"**{f['nome']}**")
                c3.write(f.get("cargo", "-"))
                c4.write(f.get("telefone") or "-")
                c5.markdown(badge_status_funcionario(f.get("status", "")), unsafe_allow_html=True)
                st.divider()
        else:
            st.info("Nenhum funcionário cadastrado no sistema.")

# ------------------------------
# FORNECEDORES
# ------------------------------
elif pagina == "🏭 Fornecedores":
    st.title("🏭 Gestão de Fornecedores")

    with st.expander("➕ Adicionar Novo Fornecedor", expanded=False):
        with st.form("form_fornecedor"):
            c1, c2 = st.columns(2)
            with c1:
                empresa = st.text_input("Nome da Empresa")
                cnpj = st.text_input("CNPJ")
            with c2:
                telefone = st.text_input("Telefone de Contato")

            if st.form_submit_button("💾 Salvar Fornecedor"):
                if not empresa:
                    st.warning("Informe o nome da empresa.")
                else:
                    ok, resp = post("/fornecedores/", {"empresa": empresa, "cnpj": cnpj, "telefone": telefone})
                    st.success(resp.get("mensagem", "Fornecedor cadastrado.")) if ok else st.error(resp.get("detail", "Erro no cadastro"))

    linha_sep()
    st.markdown('<div class="section-title">🏢 Empresas Parceiras</div>', unsafe_allow_html=True)

    dados = get("/fornecedores/")
    fornecedores = dados.get("fornecedores", [])

    if fornecedores:
        for fr in fornecedores:
            c1, c2, c3, c4 = st.columns([1, 3, 3, 3])
            c1.write(f"#{fr['id']}")
            c2.write(f"**{fr['empresa']}**")
            c3.write(fr.get("cnpj") or "-")
            c4.write(fr.get("telefone") or "-")
            st.divider()
    else:
        st.info("Nenhum fornecedor registrado.")

# ------------------------------
# VENDAS
# ------------------------------
elif pagina == "💰 Vendas":
    st.title(" 💰 Gestão de Vendas")

    meds = get("/medicamentos/").get("medicamentos", [])
    funcs = get("/funcionarios/").get("funcionarios", [])

    with st.expander("➕ Registrar Nova Venda", expanded=False):
        with st.form("form_venda"):
            c1, c2 = st.columns(2)
            mapa_med = {f"#{m['id']} - {m['nome']}": m["id"] for m in meds}
            mapa_fun = {f"#{f['id']} - {f['nome']}": f["id"] for f in funcs}

            with c1:
                med_sel = st.selectbox("Medicamento", list(mapa_med.keys()) if mapa_med else ["Sem medicamentos cadastrados"])
                qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)
            with c2:
                fun_sel = st.selectbox("Funcionário Responsável", list(mapa_fun.keys()) if mapa_fun else ["Sem funcionários cadastrados"])
                valor_total = st.number_input("Valor total da Venda (R$)", min_value=0.01, step=1.0, value=10.0)

            if st.form_submit_button("💾 Finalizar Venda"):
                if not mapa_med or not mapa_fun:
                    st.warning("Você precisa de pelo menos 1 medicamento e 1 funcionário ativos para registrar uma venda.")
                else:
                    ok, resp = post(
                        "/vendas/",
                        {
                            "medicamento_id": int(mapa_med[med_sel]),
                            "funcionario_id": int(mapa_fun[fun_sel]),
                            "quantidade": int(qtd),
                            "valor_total": float(valor_total),
                            "data_venda": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        },
                    )
                    st.success(resp.get("mensagem", "Venda registrada com sucesso!")) if ok else st.error(resp.get("detail", "Erro ao registrar venda"))

    linha_sep()
    st.markdown('<div class="section-title">🧾 Relatório de Transações</div>', unsafe_allow_html=True)

    dados = get("/vendas/")
    vendas = dados.get("vendas", [])

    if vendas:
        for v in vendas:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 3])
                c1.write(f"#{v['id']}")
                c2.write(f"**{v.get('medicamento', '-') }**")
                c3.write(f"Qtd: {v.get('quantidade', '-')}")
                c4.write(f"**R$ {float(v.get('valor_total', 0)):.2f}**")
                c5.write(f"🧑‍💼 {v.get('funcionario', '-')}")
                st.caption(f"🗓️ Data: {v.get('data_venda') or '-'}")
                st.divider()
    else:
        st.info("Nenhuma venda registrada até o momento.")

elif pagina == "📄 Documentos":
    st.title("📄 Documentos")
    st.caption("Envie PDFs, DOCX ou TXT para enriquecer a base vetorial do assistente IA.")

    with st.form("form_documentos"):
        arquivos = st.file_uploader(
            "Selecionar documentos",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="Formatos aceitos: PDF, DOCX e TXT",
        )
        submitted_docs = st.form_submit_button("📤 Enviar documentos", use_container_width=True)

    if submitted_docs:
        if not arquivos:
            st.warning("Selecione pelo menos um arquivo.")
        else:
            payload_files = []
            for arquivo in arquivos:
                mime_type = arquivo.type or "application/octet-stream"
                payload_files.append(("files", (arquivo.name, arquivo.getvalue(), mime_type)))

            with st.spinner("Indexando documentos na memória vetorial..."):
                ok, resp = post_files("/ai/documents/upload", payload_files)

            if ok:
                st.success(
                    f"{resp.get('message', 'Documentos indexados.')} ({resp.get('indexed', 0)} chunks em {resp.get('files', 0)} arquivo(s))"
                )
            else:
                st.error(resp.get("detail", "Falha ao processar documentos"))

    st.info("Depois do envio, os arquivos passam a ser consultáveis no Assistente IA junto com os dados da farmácia.")
# ------------------------------
# ASSISTENTE IA (RAG)
# ------------------------------
elif pagina == "🤖 Assistente IA":
    st.title("🤖 Assistente IA da Farmácia")
    st.caption("Consulte dados de estoque, equipe e transações através do banco inteligente (Ollama/RAG)")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Cabeçalho: Botão de sincronização e Status do Servidor
    col_sync, col_info = st.columns([1, 4])
    with col_sync:
        if st.button("🔄 Sincronizar Banco", use_container_width=True):
            with st.spinner("Lendo banco de dados e gerando vetores..."):
                try:
                    r = requests.post(f"{AI_SERVICE_URL}/ai/sync", timeout=120)
                    if r.ok:
                        st.success(f"✅ {r.json().get('indexed', 0)} registros indexados!")
                    else:
                        st.error(f"❌ Erro: {r.json().get('detail')}")
                except Exception as e:
                    st.error(f"❌ Serviço indisponível: {e}")
    
    with col_info:
        try:
            health = requests.get(f"{AI_SERVICE_URL}/ai/health", timeout=3).json()
            st.info(f"🟢 IA Online | Documentos na memória Vetorial: `{health.get('indexed_docs', '?')}`")
        except:
            st.warning("🔴 IA offline. Verifique se o backend na porta 8000 e o Ollama estão rodando.")
    
    st.divider()
    
    # Campo de input de chat
    with st.form("chat_form"):
        user_input = st.text_input("Sua pergunta:", placeholder="Ex: Quais medicamentos estão com o estoque abaixo de 10?")
        submitted = st.form_submit_button("📩 Consultar IA", use_container_width=True)
    
    # Processamento da consulta
    if submitted and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("A IA está analisando os dados da farmácia..."):
            try:
                resp = requests.post(
                    f"{AI_SERVICE_URL}/ai/chat",
                    json={"query": user_input, "top_k": 4},
                    timeout=90
                )
                if resp.ok:
                    data = resp.json()
                    st.session_state.chat_history.append({
                        "role": "ai",
                        "content": data["answer"],
                        "sources": data.get("sources", [])
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "ai",
                        "content": f"⚠️ Erro de processamento: {resp.json().get('detail')}",
                        "sources": []
                    })
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "ai",
                    "content": f"❌ Falha de conexão com o motor de IA: {e}",
                    "sources": []
                })
        st.rerun()
    
    # Renderização do histórico
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**🧑‍⚕️ Você**: {msg['content']}")
        else:
            st.markdown(f"**🤖 Assistente**: {msg['content']}")
            if msg.get("sources"):
                st.caption(f"📎 Referências utilizadas (IDs do banco): {', '.join(source.get('id', '-') for source in msg['sources'])}")
                render_chunk_sources(msg["sources"])
            st.markdown("---")
    
    # Botão para limpar a conversa
    if st.button("🗑️ Limpar histórico da conversa"):
        st.session_state.chat_history = []
        st.rerun()