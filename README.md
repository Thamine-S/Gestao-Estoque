# 📊 Análise de Previsão de Demanda e Gestão de Estoque

Este é um dashboard interativo construído com Streamlit para analisar a acurácia de previsões de demanda e otimizar a gestão de estoques. A ferramenta permite que usuários façam o upload de seus dados de vendas e previsões para gerar insights valiosos, calcular métricas de performance e obter recomendações de compra baseadas em modelos clássicos de inventário.

**[➡️ Acesse a aplicação aqui\!](https://projeto-gestao-estoque-thamine.streamlit.app)** *(Substitua pela URL do seu deploy)*

-----

## ✨ Principais Funcionalidades

  * **Upload de Dados Simplificado**: Envie um arquivo `.csv` com dados de demanda real, prevista e custos para iniciar a análise.
  * **Métricas de Acurácia**: Calcule automaticamente indicadores essenciais como `Forecast Accuracy`, `WMAPE`, `Bias` e `MAD`.
  * **Análise de Impacto Financeiro**: Quantifique o "prejuízo" gerado pelos erros de previsão para focar nos itens mais críticos.
  * **Classificação ABC**: Segmente os produtos por relevância no faturamento (`Curva ABC`) para priorizar ações.
  * **Otimização de Estoque**:
      * **Lote Econômico de Compra (LEC/EOQ)**: Descubra a quantidade ideal de compra para minimizar custos de pedido e manutenção.
      * **Estoque de Segurança e Ponto de Pedido (ROP)**: Calcule os níveis de estoque necessários para se proteger contra a variabilidade da demanda e do tempo de entrega, com base no nível de serviço desejado.
      * **Recomendação de Compra**: Obtenha uma sugestão de quantidade a ser pedida, já ajustada para o **MOQ** (Quantidade Mínima de Compra) e **Lote Múltiplo** do fornecedor.
  * **Alertas Visuais**: Identifique rapidamente quais produtos atingiram o ponto de pedido e precisam de ressuprimento.
  * **Dashboards Interativos**: Visualize os dados através de gráficos dinâmicos criados com Plotly, permitindo uma análise profunda e intuitiva.

-----

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

  * **Python**: Linguagem principal do projeto.
  * **Streamlit**: Framework utilizado para criar e fazer o deploy da interface web interativa.
  * **Pandas**: Biblioteca para manipulação e análise dos dados do arquivo CSV.
  * **Numpy**: Biblioteca para operações numéricas e cálculos matemáticos.
  * **Plotly Express**: Biblioteca para a criação dos gráficos e visualizações de dados interativas.

-----

## ⚙️ Como a Ferramenta Funciona

O fluxo de trabalho da aplicação é simples e direto:

1.  **Parâmetros de Estoque**: Na barra lateral, o usuário define os parâmetros globais para os cálculos de estoque, como custos fixos, percentual de manutenção, nível de serviço desejado e metas.
2.  **Upload do CSV**: O usuário envia um arquivo `csv` contendo os dados dos produtos.
3.  **Processamento e Cálculos**: O backend processa o arquivo e calcula todas as métricas de acurácia e os parâmetros de gestão de estoque para cada produto.
4.  **Visualização de Dados**: Os resultados são exibidos em um dashboard completo, com:
      * Indicadores de performance (KPIs).
      * Destaques para os produtos com maior impacto.
      * Uma tabela detalhada com todos os cálculos.
      * Gráficos interativos para explorar as análises visualmente.

-----

## 📂 Estrutura do Arquivo CSV

Para que a aplicação funcione corretamente, seu arquivo `.csv` deve conter as seguintes colunas:

### Colunas Obrigatórias:

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `produto` | Texto | O nome ou código único do produto (SKU). |
| `real` | Numérico | A quantidade de demanda/venda real no período. |
| `previsto` | Numérico | A quantidade de demanda prevista para o mesmo período. |
| `valor_unitario` | Numérico | O custo ou preço unitário do produto. |
| `lead_time_dias` | Numérico | O tempo de espera (em dias) entre fazer o pedido e recebê-lo. |

### Colunas Opcionais (para maior precisão):

| Coluna | Tipo | Descrição |
| :--- | :--- | :--- |
| `estoque` | Numérico | A quantidade atual de estoque disponível para o produto. |
| `desvio_padrao_demanda_diaria`| Numérico | O desvio padrão da demanda diária. Melhora o cálculo do estoque de segurança. |
| `desvio_padrao_lead_time` | Numérico | O desvio padrão do lead time (em dias). Usado na fórmula mais avançada de estoque de segurança. |

### Sample para testar:

#### Como Usar

1.  Copie o conteúdo da caixa de código abaixo.
2.  Cole em um editor de texto simples (como Bloco de Notas, VS Code, etc.).
3.  Salve o arquivo com o nome `sample_data.csv`.
4.  Acesse sua aplicação e faça o upload deste arquivo.

```csv
produto,real,previsto,valor_unitario,lead_time_dias,estoque,desvio_padrao_demanda_diaria,desvio_padrao_lead_time
Processador Alpha,50,65,1850.00,15,20,2,3
Placa de Video Beta,80,75,4500.50,30,82,3,5
Memoria RAM Gamma,350,380,320.75,10,400,10,2
SSD 1TB Delta,400,350,450.25,7,300,15,1
Fonte de Energia Epsilon,150,140,550.00,12,100,5,2
Gabinete Omega,120,150,250.00,5,150,4,1
Cooler para CPU Zeta,250,220,180.90,7,260,8,1
Placa-mae Sigma,100,90,890.80,20,95,3,4
Monitor UltraWide Kappa,75,90,2100.00,25,60,2.5,3
Teclado Mecanico Iota,500,550,480.50,5,520,12,1
Mouse Gamer Lambda,800,750,215.00,3,700,20,0.5
Parafuso M3 (Pacote 1000),15000,16000,8.50,2,20000,150,0
Cabo HDMI 2m,2500,2400,25.70,1,3000,80,0.5
Webcam Full HD,600,680,199.90,8,610,18,1
Pasta Termica Theta,1200,1000,45.10,3,950,40,1
```
-----

## 🧮 Fórmulas e Conceitos

A ferramenta utiliza conceitos consolidados de gestão de supply chain:

  * **Curva ABC**: Classificação de produtos com base no princípio de Pareto (80/20), usando o valor de consumo (`Real * Valor Unitário`) para determinar a importância de cada item.

  * **Lote Econômico de Compra (LEC/EOQ)**: Calcula a quantidade de pedido que minimiza os custos totais de inventário.
    $$LEC = \sqrt{\frac{2 \times D \times K}{H}}$$

      * $D$: Demanda Anual
      * $K$: Custo Fixo por Pedido
      * $H$: Custo de Manutenção Anual por Unidade

  * **Estoque de Segurança (SS)**: Protege contra incertezas. O cálculo se adapta aos dados disponíveis:

      * **Fórmula Avançada** (com variabilidade de demanda e lead time):
        $$SS = Z \times \sqrt{(LT \times \sigma_d^2) + (\mu_d^2 \times \sigma_{LT}^2)}$$
      * **Fórmula Padrão** (com variabilidade da demanda):
        $$SS = Z \times \sigma_d \times \sqrt{LT}$$
      * $Z$: Z-score (baseado no nível de serviço)
      * $\\sigma\_d$: Desvio Padrão da Demanda Diária
      * $LT$: Lead Time em dias
      * $\\mu\_d$: Demanda Média Diária
      * $\\sigma\_{LT}$: Desvio Padrão do Lead Time

  * **Ponto de Pedido (ROP)**: O nível de estoque que, ao ser atingido, dispara um novo pedido.
    $$ROP = (\text{Demanda Média Diária} \times LT) + SS$$

-----

> ### Projeto ainda em desenvolvimento, melhorias serão adicionadas futuramente
-----

## 🖼️ Screenshot da Aplicação

*(É altamente recomendado adicionar aqui um screenshot ou GIF da sua aplicação em funcionamento para dar uma prévia visual aos visitantes do repositório.)*

-----

Desenvolvido por **Thamine S**.
