import matplotlib.pyplot as plt

def gerar_grafico_prioridade(df):
    prioridades = df['prioridade'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 6))
    barras =ax.bar(
        prioridades.index.astype(str),
        prioridades.values
    )
    ax.set_title("Distribuição de Prioridades")
    ax.bar_label(barras)
    
    plt.tight_layout()
    return fig