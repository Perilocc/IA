from matplotlib import pyplot as plt

def gerar_grafico_risco_financeiro(df):
    risco = df['risco_financeiro'].value_counts()
    fig, ax = plt.subplots(figsize=(7, 6))
    barras =ax.bar(
        risco.index, 
        risco.values
    )
    ax.set_title("Risco Financeiro")
    ax.bar_label(barras)

    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig