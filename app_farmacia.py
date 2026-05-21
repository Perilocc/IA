import streamlit as st
import requests
from datetime import datetime, date

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(
    page_title="PMLI - Farmacia",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_URL = "http://127.0.0.1:8000"

# ------------------------------
# ESTILOS
# ------------------------------
st.markdown(
    """
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #102a43);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0;
}
.block-container {
    padding-top: 1.2rem;
}
.metric-card {
    background: linear-gradient(140deg, #102a43 0%, #0f172a 100%);
    border: 1px solid #1f4d73;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    margin-bottom: 10px;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.18);
}
.metric-card h2 {
    color: #5eead4;
    font-size: 1.95rem;
    margin: 0;
}
.metric-card p {
    color: #93c5fd;
    font-size: 0.9rem;
    margin: 0;
}
.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #0b3b5a;
    border-bottom: 2px solid #93c5fd;
    padding-bottom: 6px;
    margin-top: 6px;
    margin-bottom: 14px;
}
.status-badge {
    display: inline-block;
    padding: 4px 11px;
    border-radius: 12px;
    font-size: 0.78rem;
    font-weight: 700;
}
.badge-ativo {
    background: #134e4a;
    color: #99f6e4;
}
.badge-inativo {
    background: #7f1d1d;
    color: #fecaca;
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
        payload = r.json() if r.content else {}
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


# ------------------------------
# SIDEBAR
# ------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/pill.png", width=72)
st.sidebar.title("PMLI Farmacia")
st.sidebar.caption("Painel de Gestao da Farmacia")
st.sidebar.divider()

pagina = st.sidebar.radio(
    "Modulos",
    [
        "🏠 Dashboard",
        "💊 Medicamentos",
        "👥 Funcionarios",
        "🏭 Fornecedores",
        "💰 Vendas",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if st.sidebar.button("Testar conexao API", use_container_width=True):
    ping = get("/dashboard/")
    if ping:
        st.sidebar.success("API conectada")
    else:
        st.sidebar.error("API offline")

# ------------------------------
# DASHBOARD
# ------------------------------
if pagina == "🏠 Dashboard":
    st.title("🏠 Dashboard - Visao Geral da Farmacia")
    dados = get("/dashboard/")
    fornecedores = get("/fornecedores/").get("fornecedores", [])

    if not dados:
        st.error("Nao foi possivel conectar na API. Inicie o backend e tente novamente.")
        st.stop()

    st.markdown('<div class="section-title">Resumo Operacional</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f'<div class="metric-card"><h2>{dados["medicamentos"]["total"]}</h2><p>Medicamentos</p></div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f'<div class="metric-card"><h2>{dados["medicamentos"]["estoque_baixo"]}</h2><p>Estoque Baixo</p></div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f'<div class="metric-card"><h2>{dados["funcionarios"]["total"]}</h2><p>Funcionarios</p></div>',
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f'<div class="metric-card"><h2>{dados["vendas"]["total"]}</h2><p>Vendas</p></div>',
            unsafe_allow_html=True,
        )

    c5, c6 = st.columns(2)
    with c5:
        st.info(f"Fornecedores cadastrados: {len(fornecedores)}")
    with c6:
        hoje = datetime.now().strftime("%d/%m/%Y")
        st.success(f"Data de referencia: {hoje}")

# ------------------------------
# MEDICAMENTOS
# ------------------------------
elif pagina == "💊 Medicamentos":
    st.title("💊 Gestao de Medicamentos")

    with st.expander("➕ Novo Medicamento", expanded=False):
        with st.form("form_medicamento"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome")
                categoria = st.text_input("Categoria")
                validade = st.date_input("Validade", value=date.today())
            with c2:
                preco = st.number_input("Preco", min_value=0.01, step=0.5, value=10.0)
                estoque = st.number_input("Estoque", min_value=0, step=1, value=1)

            enviar = st.form_submit_button("💾 Salvar Medicamento")
            if enviar:
                if not nome:
                    st.warning("Informe o nome do medicamento.")
                else:
                    ok, resp = post(
                        "/medicamentos/",
                        {
                            "nome": nome,
                            "categoria": categoria,
                            "preco": float(preco),
                            "estoque": int(estoque),
                            "validade": str(validade),
                        },
                    )
                    st.success(resp.get("mensagem", "Medicamento cadastrado.")) if ok else st.error(resp.get("detail", "Erro ao cadastrar"))

    linha_sep()
    st.markdown('<div class="section-title">Lista de Medicamentos</div>', unsafe_allow_html=True)

    dados = get("/medicamentos/")
    lista = dados.get("medicamentos", [])
    apenas_estoque_baixo = st.checkbox("Mostrar apenas estoque baixo (< 10)")

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
                c5.write(f"Estoque: {med['estoque']}")
                c6.write(med.get("validade") or "-")
                st.divider()
    else:
        st.info("Nenhum medicamento encontrado.")

# ------------------------------
# FUNCIONARIOS
# ------------------------------
elif pagina == "👥 Funcionarios":
    st.title("👥 Gestao de Funcionarios")

    aba1, aba2 = st.tabs(["📋 Lista", "➕ Cadastrar"])

    with aba2:
        with st.form("form_funcionario"):
            c1, c2 = st.columns(2)
            with c1:
                nome = st.text_input("Nome completo")
                cargo = st.text_input("Cargo")
            with c2:
                telefone = st.text_input("Telefone")
                status = st.selectbox("Status", ["Ativo", "Inativo", "Ferias", "Afastado"])

            enviar = st.form_submit_button("💾 Cadastrar Funcionario")
            if enviar:
                if not nome or not cargo:
                    st.warning("Preencha nome e cargo.")
                else:
                    ok, resp = post(
                        "/funcionarios/",
                        {
                            "nome": nome,
                            "cargo": cargo,
                            "telefone": telefone,
                            "status": status,
                        },
                    )
                    st.success(resp.get("mensagem", "Funcionario cadastrado.")) if ok else st.error(resp.get("detail", "Erro no cadastro"))

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
            st.info("Nenhum funcionario encontrado.")

# ------------------------------
# FORNECEDORES
# ------------------------------
elif pagina == "🏭 Fornecedores":
    st.title("🏭 Gestao de Fornecedores")

    with st.expander("➕ Novo Fornecedor", expanded=False):
        with st.form("form_fornecedor"):
            c1, c2 = st.columns(2)
            with c1:
                empresa = st.text_input("Empresa")
                cnpj = st.text_input("CNPJ")
            with c2:
                telefone = st.text_input("Telefone")

            enviar = st.form_submit_button("💾 Salvar Fornecedor")
            if enviar:
                if not empresa:
                    st.warning("Informe o nome da empresa.")
                else:
                    ok, resp = post(
                        "/fornecedores/",
                        {
                            "empresa": empresa,
                            "cnpj": cnpj,
                            "telefone": telefone,
                        },
                    )
                    st.success(resp.get("mensagem", "Fornecedor cadastrado.")) if ok else st.error(resp.get("detail", "Erro no cadastro"))

    linha_sep()
    st.markdown('<div class="section-title">Lista de Fornecedores</div>', unsafe_allow_html=True)

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
        st.info("Nenhum fornecedor encontrado.")

# ------------------------------
# VENDAS
# ------------------------------
elif pagina == "💰 Vendas":
    st.title("💰 Gestao de Vendas")

    meds = get("/medicamentos/").get("medicamentos", [])
    funcs = get("/funcionarios/").get("funcionarios", [])

    with st.expander("➕ Nova Venda", expanded=False):
        with st.form("form_venda"):
            c1, c2 = st.columns(2)

            mapa_med = {f"#{m['id']} - {m['nome']}": m["id"] for m in meds}
            mapa_fun = {f"#{f['id']} - {f['nome']}": f["id"] for f in funcs}

            with c1:
                med_sel = st.selectbox("Medicamento", list(mapa_med.keys()) if mapa_med else ["Sem medicamentos"])
                qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)
            with c2:
                fun_sel = st.selectbox("Funcionario", list(mapa_fun.keys()) if mapa_fun else ["Sem funcionarios"])
                valor_total = st.number_input("Valor total (R$)", min_value=0.01, step=1.0, value=10.0)

            enviar = st.form_submit_button("💾 Registrar Venda")
            if enviar:
                if not mapa_med or not mapa_fun:
                    st.warning("Cadastre ao menos 1 medicamento e 1 funcionario antes de vender.")
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
                    st.success(resp.get("mensagem", "Venda registrada.")) if ok else st.error(resp.get("detail", "Erro ao registrar venda"))

    linha_sep()
    st.markdown('<div class="section-title">Historico de Vendas</div>', unsafe_allow_html=True)

    dados = get("/vendas/")
    vendas = dados.get("vendas", [])

    if vendas:
        for v in vendas:
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 3])
                c1.write(f"#{v['id']}")
                c2.write(f"**{v.get('medicamento', '-') }**")
                c3.write(f"Qtd: {v.get('quantidade', '-')}")
                c4.write(f"R$ {float(v.get('valor_total', 0)):.2f}")
                c5.write(v.get("funcionario") or "-")
                st.caption(f"Data: {v.get('data_venda') or '-'}")
                st.divider()
    else:
        st.info("Nenhuma venda registrada.")
