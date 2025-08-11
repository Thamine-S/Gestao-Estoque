import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Análise de Previsão e Estoque", layout="wide")


# --- SIDEBAR PARA INPUTS DE GESTÃO DE ESTOQUE ---
st.sidebar.header("⚙️ Parâmetros de Gestão de Estoque")

# Inputs para o Lote Econômico de Compra (LEC/EOQ)
st.sidebar.markdown("### Lote Econômico e Pedido")
custo_pedido = st.sidebar.number_input(
    "Custo Fixo por Pedido (R$)",
    min_value=0.0,
    value=50.0,
    help="Custo para processar um pedido (salários, sistema, etc.), independente da quantidade."
)
custo_manutencao_percentual = st.sidebar.slider(
    "Custo de Manutenção Anual (%)",
    min_value=0.0,
    max_value=50.0,
    value=20.0,
    step=0.5,
    help="Custo de manter o produto em estoque por um ano (armazenagem, seguro, perdas), como % do valor do produto."
)
moq_fornecedor = st.sidebar.number_input(
    "MOQ do Fornecedor (unidades)",
    min_value=0,
    value=1,
    help="Quantidade Mínima de Compra (MOQ) exigida pelo fornecedor."
)
lote_multiplo = st.sidebar.number_input(
    "Lote Múltiplo de Compra (unidades)",
    min_value=1,
    value=1,
    help="O pedido deve ser um múltiplo deste valor (ex: caixas com 12 unidades)."
)
periodos_no_ano = st.sidebar.number_input(
    "Períodos no Ano",
    min_value=1,
    value=12,
    help="Se seus dados de demanda são mensais, use 12. Se semanais, 52."
)


# Inputs para o Ponto de Pedido (ROP)
st.sidebar.markdown("### Ponto de Pedido (ROP)")
dias_no_periodo = st.sidebar.number_input(
    "Dias no Período do CSV",
    min_value=1,
    value=30,
    help="Quantos dias o seu dado de demanda 'real' representa. Ex: 30 para dados mensais."
)
nivel_servico_z = st.sidebar.selectbox(
    "Nível de Serviço Desejado",
    options=[90, 95, 98, 99],
    index=1,
    help="Probabilidade desejada de não ter ruptura de estoque durante o lead time. Afeta o estoque de segurança."
)

# Input para Meta de OTIF
st.sidebar.markdown("### Metas Operacionais")
meta_otif = st.sidebar.slider(
    "Meta de OTIF (%)",
    min_value=0.0,
    max_value=100.0,
    value=98.0,
    step=0.5,
    help="Sua meta de On-Time In-Full para o período."
)


# Mapeamento do Nível de Serviço para o Z-score
z_scores = {90: 1.28, 95: 1.65, 98: 2.05, 99: 2.33}
z_score = z_scores[nivel_servico_z]


# --- TÍTULO PRINCIPAL ---
st.title("📊 Análise de Previsão de Demanda e Gestão de Estoque")
st.write("Esta ferramenta calcula indicadores de acurácia e recomendações de estoque com base em um CSV enviado pelo usuário.")

# Explicação das fórmulas
with st.expander("🧮 Fórmulas Utilizadas (Versão Aprimorada)"):
    st.markdown("""
    - **Curva ABC**: Classificação baseada no valor de consumo acumulado (`Real * Valor Unitário`).
    
    ---
    ### Lote Econômico e Pedido Recomendado
    - **Lote Econômico de Compra (LEC/EOQ)**:
      \\[ LEC = \\sqrt{\\frac{2 \\times D \\times K}{H}} \\]
      *Onde: **D** = Demanda Anual, **K** = Custo do Pedido, **H** = Custo de Manutenção.*
    - **Pedido Recomendado**:
      1. Ajuste para MOQ: `max(LEC, MOQ)`
      2. Ajuste para Lote Múltiplo: `ceil(Ajuste_MOQ / Lote_Multiplo) * Lote_Multiplo`

    ---
    ### Ponto de Pedido e Estoque de Segurança
    O cálculo do Estoque de Segurança (SS) se adapta às colunas disponíveis no seu CSV:

    - **Fórmula Padrão (Apenas Variabilidade da Demanda)**: Requer `desvio_padrao_demanda_diaria`.
      \\[ SS = Z \\times \\sigma_d \\times \\sqrt{LT} \\]
      *Onde: **Z** = Nível de Serviço, **σd** = Desvio Padrão da Demanda Diária, **LT** = Lead Time.*

    - **Fórmula Avançada (Variabilidade de Demanda e Lead Time)**: Requer `desvio_padrao_demanda_diaria` e `desvio_padrao_lead_time`.
      \\[ SS = Z \\times \\sqrt{(LT \\times \\sigma_d^2) + (\\mu_d^2 \\times \\sigma_{LT}^2)} \\]
      *Onde: **μd** = Demanda Média Diária, **σLT** = Desvio Padrão do Lead Time.*
      
    - **Ponto de Pedido (ROP)**:
      \\[ ROP = (\\text{Demanda Média Diária} \\times LT) + SS \\]
    """)

# Upload CSV
uploaded_file = st.file_uploader(
    "📁 Envie um arquivo CSV com as colunas: 'produto', 'real', 'previsto', 'valor_unitario', 'lead_time_dias'.\n\n"
    "**Opcionais para mais precisão:** 'estoque', 'desvio_padrao_demanda_diaria', 'desvio_padrao_lead_time'.",
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Verificar colunas obrigatórias
        required_cols = {'produto', 'real', 'previsto', 'valor_unitario', 'lead_time_dias'}
        if not required_cols.issubset(df.columns):
            missing_cols = required_cols - set(df.columns)
            st.error(f"❌ O arquivo deve conter as colunas: {', '.join(missing_cols)}.")
        else:
            lista_produtos = df['produto'].unique().tolist()
            produtos_selecionados = st.multiselect(
                "**Selecione os produtos para análise:**",
                options=lista_produtos,
                default=lista_produtos,
                help="Selecione um ou mais produtos para recalcular os indicadores e gráficos."
            )
            
            if not produtos_selecionados:
                st.warning("⚠️ Por favor, selecione ao menos um produto para visualizar a análise.")
            else:
                df_filtrado = df[df['produto'].isin(produtos_selecionados)].copy()

                # --- CÁLCULOS DE ACURÁCIA ---
                df_filtrado['erro_absoluto'] = abs(df_filtrado['real'] - df_filtrado['previsto'])
                df_filtrado['bias_individual'] = df_filtrado['previsto'] - df_filtrado['real']
                df_filtrado['prejuizo'] = df_filtrado['erro_absoluto'] * df_filtrado['valor_unitario']

                # --- CÁLCULO DA CURVA ABC ---
                df_filtrado['valor_consumo'] = df_filtrado['real'] * df_filtrado['valor_unitario']
                df_filtrado = df_filtrado.sort_values(by='valor_consumo', ascending=False)
                df_filtrado['valor_acumulado'] = df_filtrado['valor_consumo'].cumsum()
                valor_total_consumo = df_filtrado['valor_consumo'].sum()
                df_filtrado['percentual_acumulado'] = (df_filtrado['valor_acumulado'] / valor_total_consumo) * 100

                def classificar_abc(percentual):
                    if percentual <= 80: return 'A'
                    elif 80 < percentual <= 95: return 'B'
                    else: return 'C'
                df_filtrado['Curva_ABC'] = df_filtrado['percentual_acumulado'].apply(classificar_abc)
                
                # --- VERIFICAÇÃO DE COLUNAS OPCIONAIS ---
                if 'estoque' not in df_filtrado.columns:
                    df_filtrado['estoque'] = 0 # Define como 0 se não existir
                    st.info("Coluna 'estoque' não encontrada. O status de ressuprimento não será calculado.")

                # --- CÁLCULOS DE GESTÃO DE ESTOQUE ---
                # Demanda Média Diária
                df_filtrado['demanda_diaria_media'] = df_filtrado['real'] / dias_no_periodo

                # Lote Econômico (LEC/EOQ)
                df_filtrado['demanda_anual'] = df_filtrado['real'] * periodos_no_ano
                df_filtrado['custo_manutencao_unidade'] = df_filtrado['valor_unitario'] * (custo_manutencao_percentual / 100)
                if custo_manutencao_percentual > 0:
                    numerador = 2 * df_filtrado['demanda_anual'] * custo_pedido
                    denominador = df_filtrado['custo_manutencao_unidade']
                    # Evitar divisão por zero ou raiz de número negativo
                    df_filtrado['LEC_EOQ'] = np.sqrt(numerador / denominador.replace(0, np.nan)).fillna(0).round(0)
                else:
                    df_filtrado['LEC_EOQ'] = np.inf

                # Pedido Recomendado (Ajustado para MOQ e Lote Múltiplo)
                df_filtrado['Pedido_Ajustado_MOQ'] = df_filtrado[['LEC_EOQ', 'produto']].apply(
                    lambda row: max(row['LEC_EOQ'], moq_fornecedor), axis=1
                )
                df_filtrado['Pedido_Recomendado'] = np.ceil(df_filtrado['Pedido_Ajustado_MOQ'] / lote_multiplo) * lote_multiplo

                # Estoque de Segurança (SS) - Lógica aprimorada
                if 'desvio_padrao_demanda_diaria' in df_filtrado.columns and 'desvio_padrao_lead_time' in df_filtrado.columns:
                    st.success("Detectadas colunas de desvio padrão da demanda e do lead time. Usando a fórmula avançada para Estoque de Segurança.")
                    # Fórmula completa
                    variancia_demanda = df_filtrado['lead_time_dias'] * (df_filtrado['desvio_padrao_demanda_diaria'] ** 2)
                    variancia_lead_time = (df_filtrado['demanda_diaria_media'] ** 2) * (df_filtrado['desvio_padrao_lead_time'] ** 2)
                    df_filtrado['estoque_seguranca'] = z_score * np.sqrt(variancia_demanda + variancia_lead_time)
                elif 'desvio_padrao_demanda_diaria' in df_filtrado.columns:
                    st.info("Detectada coluna de desvio padrão da demanda. Usando a fórmula refinada para Estoque de Segurança.")
                    # Fórmula com variabilidade da demanda
                    df_filtrado['estoque_seguranca'] = z_score * df_filtrado['desvio_padrao_demanda_diaria'] * np.sqrt(df_filtrado['lead_time_dias'])
                else:
                    st.warning("Nenhuma coluna de desvio padrão encontrada. O Estoque de Segurança será calculado de forma simplificada (menos precisa).")
                    # Fórmula original (menos precisa) como fallback
                    df_filtrado['estoque_seguranca'] = z_score * df_filtrado['demanda_diaria_media'] * np.sqrt(df_filtrado['lead_time_dias'])

                # Ponto de Pedido (ROP)
                df_filtrado['Ponto_de_Pedido'] = (df_filtrado['demanda_diaria_media'] * df_filtrado['lead_time_dias']) + df_filtrado['estoque_seguranca']
                df_filtrado['Ponto_de_Pedido'] = df_filtrado['Ponto_de_Pedido'].round(0)

                # Alerta de Ressuprimento
                df_filtrado['Status_Estoque'] = np.where(df_filtrado['estoque'] <= df_filtrado['Ponto_de_Pedido'], 'PEDIR AGORA!', 'OK')


                # --- MÉTRICAS GERAIS ---
                soma_erro = df_filtrado['erro_absoluto'].sum()
                soma_real = df_filtrado['real'].abs().sum()
                wmape = (soma_erro / soma_real) * 100 if soma_real != 0 else 0
                fa = 100 - wmape
                bias_total = df_filtrado['bias_individual'].sum()
                mad = np.mean(df_filtrado['erro_absoluto'])

                # Cálculo do Giro de Estoque
                valor_vendas_total = (df_filtrado['real'] * df_filtrado['valor_unitario']).sum()
                valor_estoque_total = (df_filtrado['estoque'] * df_filtrado['valor_unitario']).sum()
                giro_estoque = valor_vendas_total / valor_estoque_total if valor_estoque_total > 0 else 0

                
                
                
                  # SEÇÃO DE DESTAQUES
                st.markdown("---")
                st.subheader("🔍 Destaques da Análise")
                maior_erro_prod = df_filtrado.loc[df_filtrado['erro_absoluto'].idxmax()]
                menor_erro_prod = df_filtrado.loc[df_filtrado['erro_absoluto'].idxmin()]
                maior_prejuizo_prod = df_filtrado.loc[df_filtrado['prejuizo'].idxmax()]

                col_destaque1, col_destaque2, col_destaque3 = st.columns(3)
                with col_destaque1:
                    st.markdown(f"##### 🎯 Maior Prejuízo")
                    st.metric(
                        label=maior_prejuizo_prod['produto'],
                        value=f"R$ {maior_prejuizo_prod['prejuizo']:,.2f}",
                        help=f"Este produto sozinho gerou o maior impacto financeiro negativo devido ao erro de previsão."
                    )
                with col_destaque2:
                    st.markdown(f"##### 👎 Maior Erro (unidades)")
                    st.metric(
                        label=maior_erro_prod['produto'],
                        value=f"{maior_erro_prod['erro_absoluto']:,.0f} un.",
                        help="Este produto teve a maior diferença absoluta entre a venda real e a prevista."
                    )
                with col_destaque3:
                    st.markdown(f"##### 👍 Menor Erro (unidades)")
                    st.metric(
                        label=menor_erro_prod['produto'],
                        value=f"{menor_erro_prod['erro_absoluto']:,.0f} un.",
                        help="Este produto teve a previsão mais próxima da realidade em unidades."
                    )
                    
                    
                # --- LAYOUT DE EXIBIÇÃO ---
                st.markdown("---")
                # --- PAINEL DE INDICADORES ---
                st.subheader("📈 Indicadores de Performance")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Forecast Accuracy", f"{fa:.2f} %", help="Acurácia: 100% - WMAPE")
                    st.metric("WMAPE", f"{wmape:.2f} %", help="Erro Percentual Médio Ponderado")
                with col2:
                    st.metric("Bias Total", f"{bias_total:.2f} un.", help="Viés da previsão. Positivo = Superestimado (Otimista)")
                    st.metric("Prejuízo Total", f"R$ {df_filtrado['prejuizo'].sum():,.2f}", help="Soma do impacto financeiro dos erros")
                with col3:
                    st.metric("Giro de Estoque", f"{giro_estoque:.2f}", help="Vendas / Estoque Médio (em valor)")
                    st.metric("MAD", f"{mad:.2f}", help="Erro médio absoluto em unidades.")
                with col4:
                    st.metric("Meta de OTIF", f"{meta_otif:.1f} %", help="% de pedidos que devem ser entregues no prazo e completos.")
                    st.metric("Itens para Pedir Agora", f"{df_filtrado[df_filtrado['Status_Estoque'] == 'PEDIR AGORA!'].shape[0]}", help="Produtos abaixo do ponto de pedido.")

                st.markdown("---")

                # --- TABELA DETALHADA ---
                st.subheader("📋 Análise Detalhada por Produto")
                colunas_para_exibir = [
                    'produto', 'Curva_ABC', 'real', 'previsto', 'erro_absoluto', 'prejuizo',
                    'estoque_seguranca', 'Ponto_de_Pedido', 'LEC_EOQ', 'Pedido_Recomendado', 'estoque', 'Status_Estoque'
                ]
                # Arredondar colunas para melhor visualização
                df_display = df_filtrado[colunas_para_exibir].copy()
                df_display['estoque_seguranca'] = df_display['estoque_seguranca'].round(1)
                st.dataframe(df_display)




                # --- GRÁFICOS DE GESTÃO DE ESTOQUE ---
                st.markdown("---")
                st.subheader("📦 Gráficos de Gestão de Estoque")

                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    st.markdown("<h6>Distribuição do Valor por Classe ABC</h6>", unsafe_allow_html=True)
                    abc_summary = df_filtrado.groupby('Curva_ABC')['valor_consumo'].sum().reset_index()
                    fig_abc = px.pie(abc_summary, values='valor_consumo', names='Curva_ABC', 
                                     color='Curva_ABC', color_discrete_map={'A':'#4CAF50', 'B':'#FFC107', 'C':'#F44336'})
                    fig_abc.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig_abc, use_container_width=True)

                with col_g2:
                    st.markdown("<h6>Estoque Atual vs. Ponto de Pedido (Itens Críticos)</h6>", unsafe_allow_html=True)
                    df_status = df_filtrado[df_filtrado['Status_Estoque'] == 'PEDIR AGORA!'].sort_values(by='valor_consumo', ascending=False).head(15)
                    if not df_status.empty:
                        fig_rop = px.bar(df_status, x='produto', y=['estoque', 'Ponto_de_Pedido'],
                                         barmode='group', labels={'value': 'Quantidade', 'variable': 'Métrica'},
                                         color_discrete_map={'estoque':'lightblue', 'Ponto_de_Pedido':'salmon'})
                        fig_rop.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig_rop, use_container_width=True)
                    else:
                        st.success("✅ Todos os itens estão com estoque acima do Ponto de Pedido.")

                # --- GRÁFICOS DE ACURÁCIA DA PREVISÃO ---
                st.markdown("---")
                st.subheader("📊 Gráficos de Acurácia da Previsão")
                
                col_g3, col_g4 = st.columns(2)
                with col_g3:
                    st.markdown("<h6>Prejuízo por Produto (Top 20)</h6>", unsafe_allow_html=True)
                    df_plot = df_filtrado.sort_values('prejuizo', ascending=False).head(20)
                    fig_prejuizo = px.bar(df_plot, x='produto', y='prejuizo', color='Curva_ABC',
                                          color_discrete_map={'A':'#4CAF50', 'B':'#FFC107', 'C':'#F44336'})
                    st.plotly_chart(fig_prejuizo, use_container_width=True)

                with col_g4:
                    st.markdown("<h6>Dispersão: Previsto vs. Real</h6>", unsafe_allow_html=True)
                    scatter_fig = px.scatter(df_filtrado, x='real', y='previsto', color='Curva_ABC', size='prejuizo', hover_name='produto',
                                             labels={'real': 'Valor Real', 'previsto': 'Valor Previsto'},
                                             color_discrete_map={'A':'#4CAF50', 'B':'#FFC107', 'C':'#F44336'})
                    max_val = max(df_filtrado['real'].max(), df_filtrado['previsto'].max()) * 1.05
                    scatter_fig.add_shape(type='line', x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color='gray', dash='dash'))
                    st.plotly_chart(scatter_fig, use_container_width=True)
                    with st.expander("📖 Explicação do Gráfico"):
                        st.markdown("""
                        Plota cada produto como um ponto (valor real no eixo X, previsto no eixo Y). A linha cinza representa a previsão perfeita.
                        - **Pontos acima da linha**: Superestimação (viés otimista).
                        - **Pontos abaixo da linha**: Subestimação (viés pessimista).
                        - **Tamanho da bolha**: Representa o prejuízo financeiro do erro.
                        """)
                    
                col_g5, col_g6 = st.columns(2)
                with col_g5:
                    st.markdown("<h6>Distribuição de Prejuízo por Classe e Produto</h6>", unsafe_allow_html=True)
                    st.plotly_chart(px.treemap(df_filtrado, path=[px.Constant("Todos"), 'Curva_ABC', 'produto'], values='prejuizo',
                                               color='Curva_ABC', color_discrete_map={'(?)':'#262730', 'A':'#4CAF50', 'B':'#FFC107', 'C':'#F44336'}),
                                    use_container_width=True)
                    with st.expander("📖 Explicação do Gráfico"):
                        st.markdown("""
                        Visualiza a hierarquia do **prejuízo total**, quebrando-o por Classe ABC e, em seguida, por produto. 
                        Permite identificar rapidamente qual classe e quais produtos específicos são os maiores contribuintes para as perdas financeiras.
                        """)

                with col_g6:
                    st.markdown("<h6>Real vs. Previsto (Top 20)</h6>", unsafe_allow_html=True)
                    df_plot = df_filtrado.head(20) # Already sorted by valor_consumo
                    df_melted = df_plot.melt(id_vars='produto', value_vars=['real', 'previsto'], var_name='tipo', value_name='valor')
                    st.plotly_chart(px.bar(df_melted, x='produto', y='valor', color='tipo', barmode='group'), use_container_width=True)
                    with st.expander("📖 Explicação do Gráfico"):
                        st.markdown("""
                        Compara lado a lado os valores **reais** e **previstos** para cada produto, permitindo uma análise visual direta da magnitude e direção do erro para os itens mais relevantes em valor.
                        """)

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.info("Aguardando o envio de um arquivo CSV para iniciar a análise.")

# --- RODAPÉ ---
st.markdown("---")
st.caption("Desenvolvido com ❤️ usando Streamlit e Plotly")
