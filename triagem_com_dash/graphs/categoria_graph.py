import matplotlib.pyplot as plt

def gerar_grafico_categoria(df):
    categorias = df['categoria'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 6))
    barras = ax.bar(
        categorias.index, 
        categorias.values
    )
    ax.set_title("Processos por Categoria")
    ax.bar_label(barras)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig