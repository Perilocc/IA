from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI(title="API Farmácia", version="2.0")


# ─────────────────────────────────────────────
# BANCO DE DADOS
# ─────────────────────────────────────────────

def db_connection():
    conn = sqlite3.connect("farmacia.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Medicamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            validade TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # Funcionários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT NOT NULL,
            telefone TEXT,
            status TEXT DEFAULT 'Ativo',
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # Fornecedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
            cnpj TEXT UNIQUE,
            telefone TEXT,
            criado_em TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # Vendas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicamento_id INTEGER,
            funcionario_id INTEGER,
            quantidade INTEGER,
            valor_total REAL,
            data_venda TEXT,
            FOREIGN KEY (medicamento_id)
                REFERENCES medicamentos(id),

            FOREIGN KEY (funcionario_id)
                REFERENCES funcionarios(id)
        )
    """)

    conn.commit()
    return conn


# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class Medicamento(BaseModel):
    nome: str
    categoria: str
    preco: float
    estoque: int
    validade: Optional[str] = None


class Funcionario(BaseModel):
    nome: str
    cargo: str
    telefone: Optional[str] = None
    status: Optional[str] = "Ativo"


class Fornecedor(BaseModel):
    empresa: str
    cnpj: str
    telefone: Optional[str] = None


class Venda(BaseModel):
    medicamento_id: int
    funcionario_id: int
    quantidade: int
    valor_total: float
    data_venda: Optional[str] = None


# ─────────────────────────────────────────────
# MEDICAMENTOS
# ─────────────────────────────────────────────

@app.post("/medicamentos/")
def criar_medicamento(med: Medicamento):

    conn = db_connection()

    conn.execute("""
        INSERT INTO medicamentos
        (nome,categoria,preco,estoque,validade)
        VALUES (?,?,?,?,?)
    """,
    (
        med.nome,
        med.categoria,
        med.preco,
        med.estoque,
        med.validade
    ))

    conn.commit()

    return {"mensagem":"Medicamento cadastrado"}


@app.get("/medicamentos/")
def listar_medicamentos():

    conn = db_connection()

    rows = conn.execute(
        "SELECT * FROM medicamentos"
    ).fetchall()

    return {
        "medicamentos":[dict(r) for r in rows]
    }


# ─────────────────────────────────────────────
# FUNCIONÁRIOS
# ─────────────────────────────────────────────

@app.post("/funcionarios/")
def criar_funcionario(func:Funcionario):

    conn=db_connection()

    conn.execute("""
        INSERT INTO funcionarios
        (nome,cargo,telefone,status)
        VALUES (?,?,?,?)
    """,
    (
        func.nome,
        func.cargo,
        func.telefone,
        func.status
    ))

    conn.commit()

    return {"mensagem":"Funcionário cadastrado"}


@app.get("/funcionarios/")
def listar_funcionarios():

    conn=db_connection()

    rows=conn.execute(
        "SELECT * FROM funcionarios"
    ).fetchall()

    return {
        "funcionarios":[dict(r) for r in rows]
    }


# ─────────────────────────────────────────────
# FORNECEDORES
# ─────────────────────────────────────────────

@app.post("/fornecedores/")
def criar_fornecedor(fornecedor:Fornecedor):

    conn=db_connection()

    try:

        conn.execute("""
            INSERT INTO fornecedores
            (empresa,cnpj,telefone)
            VALUES (?,?,?)
        """,
        (
            fornecedor.empresa,
            fornecedor.cnpj,
            fornecedor.telefone
        ))

        conn.commit()

        return {"mensagem":"Fornecedor cadastrado"}

    except sqlite3.IntegrityError:

        raise HTTPException(
            status_code=400,
            detail="CNPJ já cadastrado"
        )


@app.get("/fornecedores/")
def listar_fornecedores():

    conn=db_connection()

    rows=conn.execute(
        "SELECT * FROM fornecedores"
    ).fetchall()

    return {
        "fornecedores":[dict(r) for r in rows]
    }


# ─────────────────────────────────────────────
# VENDAS
# ─────────────────────────────────────────────

@app.post("/vendas/")
def criar_venda(venda:Venda):

    conn=db_connection()

    conn.execute("""
        INSERT INTO vendas
        (medicamento_id,
         funcionario_id,
         quantidade,
         valor_total,
         data_venda)

        VALUES (?,?,?,?,?)
    """,

    (
        venda.medicamento_id,
        venda.funcionario_id,
        venda.quantidade,
        venda.valor_total,
        venda.data_venda
    ))

    conn.commit()

    return {"mensagem":"Venda registrada"}


@app.get("/vendas/")
def listar_vendas():

    conn=db_connection()

    rows=conn.execute("""

        SELECT
            v.*,
            m.nome AS medicamento,
            f.nome AS funcionario

        FROM vendas v

        LEFT JOIN medicamentos m
        ON m.id=v.medicamento_id

        LEFT JOIN funcionarios f
        ON f.id=v.funcionario_id

    """).fetchall()

    return {
        "vendas":[dict(r) for r in rows]
    }


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@app.get("/dashboard/")
def dashboard():

    conn=db_connection()

    total_medicamentos=conn.execute(
        "SELECT COUNT(*) FROM medicamentos"
    ).fetchone()[0]

    estoque_baixo=conn.execute(
        "SELECT COUNT(*) FROM medicamentos WHERE estoque < 10"
    ).fetchone()[0]

    total_funcionarios=conn.execute(
        "SELECT COUNT(*) FROM funcionarios"
    ).fetchone()[0]

    total_vendas=conn.execute(
        "SELECT COUNT(*) FROM vendas"
    ).fetchone()[0]

    return {

        "medicamentos":{
            "total":total_medicamentos,
            "estoque_baixo":estoque_baixo
        },

        "funcionarios":{
            "total":total_funcionarios
        },

        "vendas":{
            "total":total_vendas
        }
    }