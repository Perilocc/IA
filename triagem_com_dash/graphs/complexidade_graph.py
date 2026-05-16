import matplotlib.pyplot as plt

def gerar_grafico_complexidade(df):
    complexidade = df['complexidade'].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    total = complexidade.sum()
    ax.pie(
        complexidade.values,
        labels=complexidade.index,
        autopct=lambda pct: f'{pct:.1f}%\n({int(round(pct/100 * total))})'
    )
    ax.set_title("Complexidade dos Processos")
    
    plt.tight_layout()
    return fig