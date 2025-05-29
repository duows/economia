# Dashboard de Análise Macroeconômica Comparativa Global

## Descrição

Este projeto consiste em um dashboard interativo desenvolvido com Streamlit e Python para a análise comparativa de indicadores macroeconômicos chave de diversos países ao longo do tempo. O objetivo é permitir a exploração visual de dados como PIB per capita, investimento em educação e métricas de industrialização, facilitando a identificação de tendências, comparações e possíveis correlações, com um foco particular em contextualizar a posição do Brasil nesse cenário global.

## Funcionalidades

* **Carregamento de Dados Locais:** O dashboard é projetado para carregar dados a partir de arquivos CSV armazenados localmente.
* **Filtros Interativos:**
    * Seleção de múltiplos países para análise comparativa.
    * Seleção de um ano específico para visualizações pontuais e cálculo de correlações.
* **Visualizações Diversificadas:**
    * **Logs de Carregamento:** Feedback sobre o status do carregamento de cada arquivo de dados.
    * **Comparativo Pontual:**
        * Tabela de dados para os países e ano selecionados.
        * Gráfico de Barras comparando um indicador entre os países.
        * Gráfico de Dispersão para explorar a relação entre dois indicadores.
    * **Análise de Desenvolvimento ao Longo do Tempo:**
        * Gráfico de Linhas para visualizar a evolução de múltiplos indicadores para um único país selecionado.
        * Tabela de Série Temporal mostrando um indicador para os países selecionados, com anos nas colunas.
        * Mapa de Calor (Heatmap) representando visualmente a tabela de série temporal.
    * **Matriz de Correlação:** Heatmap mostrando a correlação de Pearson entre todos os indicadores disponíveis para os países e ano selecionados.

## Dados

O dashboard utiliza arquivos CSV que devem ser baixados manualmente e colocados em uma pasta chamada `dados_baixados` (localizada no mesmo diretório que o script `dashboard.py`).

**Arquivos CSV Esperados e Indicadores Correspondentes:**

1.  **`banco_mundial_pib_per_capita_ppp.csv`**: Contendo "PIB per capita (PPP Dólar)".
    * Fonte: Banco Mundial (Indicador: `NY.GDP.PCAP.PP.CD`).
2.  **`banco_mundial_gasto_educ_perc_pib.csv`**: Contendo "Gasto em Educação (% PIB)".
    * Fonte: Banco Mundial (Indicador: `SE.XPD.TOTL.GD.ZS`).
3.  **`banco_mundial_industria_perc_pib.csv`**: Contendo "Indústria (% PIB)".
    * Fonte: Banco Mundial (Indicador: `NV.IND.TOTL.ZS`).
4.  **`banco_mundial_manuf_export_perc.csv`**: Contendo "Manufaturados nas Exportações (%)".
    * Fonte: Banco Mundial (Indicador: `TX.VAL.MANF.ZS.UN`).
5.  **`banco_mundial_manufatura_perc_pib.csv`**: Contendo "Manufatura (% PIB)".
    * Fonte: Banco Mundial (Indicador: `NV.IND.MANF.ZS`).

**Indicadores Adicionais (Carregamento Opcional de Arquivo + Dados Pontuais):**

6.  **`Gasto por Aluno (PPP Dólar)`**:
    * O script tentará carregar `ocde_gasto_aluno_ppp.csv` da pasta `dados_baixados` se existir (fonte: OCDE, "Education at a Glance").
    * Adicionalmente, dados pontuais para Brasil (2020: 4306 USD) e EUA (2020: 19973 USD) são incluídos diretamente no código e combinados com os dados do arquivo, se este for carregado.

**Instruções para Baixar os Dados Manualmente:**
Consulte as instruções detalhadas fornecidas anteriormente sobre como navegar nos sites do Banco Mundial, OCDE, etc., para baixar os arquivos CSV corretos (geralmente os arquivos de "Data" dentro dos ZIPs do Banco Mundial) e renomeá-los conforme a lista acima.

## Setup e Instalação

### Pré-requisitos

* Python 3.7 ou superior.
* pip (gerenciador de pacotes Python).

### Passos

1.  **Clone ou baixe este projeto:**
    Se você tiver o `dashboard.py` e os arquivos de dados, pode pular esta etapa.

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    ```bash
    python -m venv venv
    # No Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    Crie um arquivo chamado `requirements.txt` (veja a seção abaixo) na pasta raiz do projeto e execute:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare os Dados:**
    * Crie uma pasta chamada `dados_baixados` na raiz do projeto.
    * Baixe os arquivos CSV conforme descrito na seção "Dados" e coloque-os dentro da pasta `dados_baixados` com os nomes especificados.

