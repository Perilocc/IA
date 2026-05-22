import sqlite3

DATABASE_NAME = "farmacia.db"

def db_connection():
    conn = sqlite3.connect(
        DATABASE_NAME
    )
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = db_connection()
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
            criado_em TEXT DEFAULT (
                datetime('now','localtime')
            )
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
            criado_em TEXT DEFAULT (
                datetime('now','localtime')
            )
        )
    """)

    # Fornecedores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
            cnpj TEXT UNIQUE,
            telefone TEXT,
            criado_em TEXT DEFAULT (
                datetime('now','localtime')
            )
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
    conn.close()