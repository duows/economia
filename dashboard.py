import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import time
import os

# --- 0. CONFIGURAÇÃO DA PÁGINA STREAMLIT ---
st.set_page_config(layout="wide", page_title="Dashboard Macroeconômico Comparativo")

# --- 1. CONFIGURAÇÕES ---
CAMINHO_PASTA_DADOS = "dados_baixados"
PAISES_INTERESSE_WB_ORIGINAL = [
    'Brazil', 'United States', 'Germany', 'Korea, Rep.', 'China', 'India',
    'South Africa', 'Russian Federation', 'Mexico', 'Argentina', 'Chile',
    'Colombia', 'Ireland', 'Vietnam'
]
MAPA_NOMES_PAISES = {
    'Korea, Rep.': 'Coreia do Sul',
    'United States': 'EUA',
    'Russian Federation': 'Rússia',
    'Brazil': 'Brasil'
}
PAISES_DASHBOARD = sorted([MAPA_NOMES_PAISES.get(p, p) for p in PAISES_INTERESSE_WB_ORIGINAL])
ANOS_RANGE = (2010, 2023)

# --- 2. FUNÇÕES PARA PROCESSAMENTO DE DADOS (mantidas da sua última versão) ---
def processar_df_banco_mundial(df_raw, nome_novo_indicador, paises_interesse_original_wb, anos_range_tuple, mapa_nomes):
    cols_anos = [str(ano) for ano in range(anos_range_tuple[0], anos_range_tuple[1] + 1)]
    cols_anos_existentes = [col for col in cols_anos if col in df_raw.columns]
    
    if 'Country Name' not in df_raw.columns:
        print(f"AVISO: Coluna 'Country Name' não encontrada no arquivo para {nome_novo_indicador}.")
        return pd.DataFrame(columns=['País', 'Ano', nome_novo_indicador])
        
    if not cols_anos_existentes:
        print(f"AVISO: Nenhuma coluna de ano no intervalo {anos_range_tuple} encontrada para {nome_novo_indicador}. Países no arquivo: {df_raw['Country Name'].unique()[:5]}")
        return pd.DataFrame(columns=['País', 'Ano', nome_novo_indicador])

    cols_to_keep = ['Country Name'] + cols_anos_existentes
    df_processed_subset = df_raw[cols_to_keep]
    df_processed_subset = df_processed_subset[df_processed_subset['Country Name'].isin(paises_interesse_original_wb)]
    
    if df_processed_subset.empty:
        return pd.DataFrame(columns=['País', 'Ano', nome_novo_indicador])

    df_long = pd.melt(df_processed_subset, id_vars=['Country Name'], value_vars=cols_anos_existentes,
                      var_name='Ano', value_name=nome_novo_indicador)
    
    df_long['Ano'] = pd.to_numeric(df_long['Ano'])
    df_long[nome_novo_indicador] = pd.to_numeric(df_long[nome_novo_indicador], errors='coerce')
    
    df_long['País'] = df_long['Country Name'].map(mapa_nomes).fillna(df_long['Country Name'])
    df_long = df_long.drop(columns=['Country Name'])
    
    return df_long[['País', 'Ano', nome_novo_indicador]]

def ler_csv_local(caminho_arquivo, nome_novo_indicador, paises_interesse_original_wb, anos_range_tuple, mapa_nomes, skiprows=4, encoding='latin1'):
    abs_path = os.path.abspath(caminho_arquivo)
    print(f"Tentando ler arquivo local: {abs_path} para {nome_novo_indicador}...")
    try:
        df_raw = pd.read_csv(caminho_arquivo, skiprows=skiprows, encoding=encoding)
        df_processed = processar_df_banco_mundial(df_raw, nome_novo_indicador, paises_interesse_original_wb, anos_range_tuple, mapa_nomes)
        
        if df_processed.empty:
            msg = f"ℹ️ Nenhum dado processado para '{nome_novo_indicador}' do arquivo '{os.path.basename(caminho_arquivo)}' para os países/anos de interesse."
            if 'Country Name' in df_raw.columns and df_raw['Country Name'].isin(paises_interesse_original_wb).any():
                 msg = f"⚠️ Países de interesse existem em '{os.path.basename(caminho_arquivo)}' para '{nome_novo_indicador}', mas o processamento resultou em dados vazios (verifique anos/valores no CSV)."
            print(msg)
            return None, msg
        
        msg = f"✔️ '{nome_novo_indicador}' lido do arquivo: {os.path.basename(caminho_arquivo)}"
        print(msg)
        return df_processed, msg
    except FileNotFoundError:
        error_message = f"❌ ARQUIVO NÃO ENCONTRADO: {abs_path}. Indicador '{nome_novo_indicador}' não será carregado."
        print(error_message)
        return None, error_message
    except Exception as e:
        error_message = f"❌ Erro ao ler ou processar {abs_path} para '{nome_novo_indicador}': {e}. Indicador não será carregado."
        print(error_message)
        return None, error_message

arquivos_a_carregar = {
    'banco_mundial_pib_per_capita_ppp.csv': 'PIB per capita (PPP Dólar)',
    'banco_mundial_gasto_educ_perc_pib.csv': 'Gasto em Educação (% PIB)',
    'banco_mundial_industria_perc_pib.csv': 'Indústria (% PIB)',
    'banco_mundial_manuf_export_perc.csv': 'Manufaturados nas Exportações (%)',
    'banco_mundial_manufatura_perc_pib.csv': 'Manufatura (% PIB)'
}

@st.cache_data(ttl=3600)
def carregar_todos_os_dados():
    lista_dfs_carregados = []
    mensagens_status = []
    
    for nome_arquivo, nome_indicador in arquivos_a_carregar.items():
        caminho_completo = os.path.join(CAMINHO_PASTA_DADOS, nome_arquivo)
        df_indicador, msg = ler_csv_local(caminho_completo, nome_indicador, PAISES_INTERESSE_WB_ORIGINAL, ANOS_RANGE, MAPA_NOMES_PAISES)
        mensagens_status.append(msg)
        if df_indicador is not None and not df_indicador.empty:
            lista_dfs_carregados.append(df_indicador)

    df_gasto_aluno_nome = 'Gasto por Aluno (PPP Dólar)'
    caminho_gasto_aluno_csv = os.path.join(CAMINHO_PASTA_DADOS, 'ocde_gasto_aluno_ppp.csv')
    df_gasto_aluno_csv, msg_gasto_csv = ler_csv_local(caminho_gasto_aluno_csv, df_gasto_aluno_nome, PAISES_INTERESSE_WB_ORIGINAL, ANOS_RANGE, MAPA_NOMES_PAISES)
    mensagens_status.append(msg_gasto_csv)

    dados_reais_gasto_aluno_pontuais_df = pd.DataFrame([
        {'País': 'Brasil', 'Ano': 2020, df_gasto_aluno_nome: 4306},
        {'País': 'EUA', 'Ano': 2020, df_gasto_aluno_nome: 19973},
    ])
    
    df_gasto_aluno_final_para_merge = pd.DataFrame()
    if df_gasto_aluno_csv is not None and not df_gasto_aluno_csv.empty:
        df_gasto_aluno_csv['Ano'] = df_gasto_aluno_csv['Ano'].astype(int)
        dados_reais_gasto_aluno_pontuais_df['Ano'] = dados_reais_gasto_aluno_pontuais_df['Ano'].astype(int)
        df_gasto_aluno_final_para_merge = pd.concat([dados_reais_gasto_aluno_pontuais_df, df_gasto_aluno_csv]).drop_duplicates(subset=['País', 'Ano'], keep='last')
        mensagens_status.append(f"✔️ Dados de '{df_gasto_aluno_nome}' do arquivo (se existente) foram combinados com dados pontuais.")
    else:
        df_gasto_aluno_final_para_merge = dados_reais_gasto_aluno_pontuais_df
        mensagens_status.append(f"✔️ Apenas dados pontuais para '{df_gasto_aluno_nome}' carregados (arquivo 'ocde_gasto_aluno_ppp.csv' não encontrado/vazio ou erro).")
    
    if not df_gasto_aluno_final_para_merge.empty:
        lista_dfs_carregados.append(df_gasto_aluno_final_para_merge)
        
    anos_todos = list(range(ANOS_RANGE[0], ANOS_RANGE[1] + 1))
    df_final = pd.DataFrame([(pais, ano) for pais in PAISES_DASHBOARD for ano in anos_todos], columns=['País', 'Ano'])

    if not lista_dfs_carregados:
        print("Nenhum DataFrame de indicador foi carregado de arquivos.")
        return df_final, mensagens_status

    for df_to_merge in lista_dfs_carregados:
        if df_to_merge is not None and not df_to_merge.empty:
            df_to_merge['Ano'] = pd.to_numeric(df_to_merge['Ano'], errors='coerce').dropna().astype(int)
            df_to_merge = df_to_merge.dropna(subset=['País'])
            if not df_to_merge.empty:
                 df_final = pd.merge(df_final, df_to_merge, on=['País', 'Ano'], how='left')
    
    df_final = df_final.sort_values(by=['País', 'Ano']).reset_index(drop=True)
    return df_final, mensagens_status

# --- CORPO PRINCIPAL DO APP STREAMLIT ---
st.title("Análise Macroeconômica Comparativa Global 🌎")
df_dados, mensagens_carregamento = carregar_todos_os_dados()

with st.expander("Logs de Carregamento de Dados", expanded=False):
    for msg in mensagens_carregamento:
        if "✔️" in msg: st.success(msg)
        elif "⚠️" in msg: st.warning(msg)
        elif "❌" in msg: st.error(msg)
        else: st.info(msg)

if df_dados.empty or len(df_dados.columns) <= 2:
    st.error("Não foi possível carregar dados para os indicadores. Verifique os arquivos CSV na pasta 'dados_baixados' e os logs no console.")
else:
    st.markdown("""
    Este dashboard permite a análise comparativa de indicadores macroeconômicos chave.
    Os dados são lidos de arquivos CSV locais. Indicadores/países sem dados aparecerão como 'NaN' ou podem ser omitidos dos gráficos se não houver dados válidos.
    """)

    st.sidebar.header("Filtros de Análise")
    paises_disponiveis_no_df = sorted(df_dados['País'].dropna().unique())
    default_countries_candidates = ['Brasil', 'China', 'EUA'] 
    default_countries = [p for p in default_countries_candidates if p in paises_disponiveis_no_df]
    if not default_countries and paises_disponiveis_no_df:
        default_countries = [paises_disponiveis_no_df[0]]

    paises_selecionados_gerais = st.sidebar.multiselect( 
        "Selecione os Países:", paises_disponiveis_no_df, default=default_countries, key="paises_gerais_v5" # Chave atualizada
    )

    anos_disponiveis_no_df = sorted(df_dados['Ano'].dropna().astype(int).unique(), reverse=True)
    ano_selecionado_pontual = None 
    if anos_disponiveis_no_df:
        default_ano_index = 0
        try: 
            if 2023 in anos_disponiveis_no_df: 
                default_ano_index = anos_disponiveis_no_df.index(2023)
        except ValueError:
            pass 

        ano_selecionado_pontual = st.sidebar.selectbox(
            "Selecione o Ano (para comparações pontuais e correlação):", anos_disponiveis_no_df, index=default_ano_index, key="ano_pontual_corr"
        )
    else:
        st.sidebar.warning("Nenhum ano disponível.")

    indicadores_disponiveis_df = [col for col in df_dados.columns if col not in ['País', 'Ano']]

    if not paises_selecionados_gerais or ano_selecionado_pontual is None:
        if not (df_dados.empty or len(df_dados.columns) <=2):
             st.warning("Selecione países e um ano para visualizar as comparações pontuais.")
    else:
        df_filtrado_ano_pontual = df_dados[
            (df_dados['País'].isin(paises_selecionados_gerais)) &
            (df_dados['Ano'] == ano_selecionado_pontual)
        ].copy()
        
        st.markdown("---")
        st.header(f"Comparativo Pontual para o Ano de {ano_selecionado_pontual}")
        st.subheader("Tabela de Dados Comparativa")
        
        if not df_filtrado_ano_pontual.empty:
            df_tabela_display = df_filtrado_ano_pontual.dropna(subset=indicadores_disponiveis_df, how='all')
            if not df_tabela_display.empty:
                cols_para_tabela = ['País'] + [ind for ind in indicadores_disponiveis_df if ind in df_tabela_display.columns]
                st.dataframe(df_tabela_display[cols_para_tabela].set_index('País').style.format(na_rep="-", precision=2))
            else:
                st.info(f"Nenhum país com dados para os indicadores no ano {ano_selecionado_pontual}.")
        else:
            st.info(f"Nenhum dado para a combinação de filtros no ano {ano_selecionado_pontual}.")

        col_vis1, col_vis2 = st.columns(2)
        indicadores_com_dados_ano_pontual = [ind for ind in indicadores_disponiveis_df if ind in df_filtrado_ano_pontual.columns and df_filtrado_ano_pontual[ind].notna().any()]

        with col_vis1:
            st.subheader("Comparativo por Indicador (Gráfico de Barras)")
            if indicadores_com_dados_ano_pontual:
                indicador_barras = st.selectbox("Indicador:", indicadores_com_dados_ano_pontual, key="bar_ind_pontual_v5")
                if indicador_barras:
                    df_barras_valid = df_filtrado_ano_pontual.dropna(subset=[indicador_barras])
                    if not df_barras_valid.empty:
                        fig_barras = px.bar(df_barras_valid.sort_values(by=indicador_barras, ascending=False),
                            x='País', y=indicador_barras, color='País', title=f"{indicador_barras} em {ano_selecionado_pontual}")
                        st.plotly_chart(fig_barras, use_container_width=True)
                    else: st.info(f"Sem dados para '{indicador_barras}' nos filtros atuais.")
            else: st.info("Sem indicadores com dados para este ano/seleção (gráfico de barras).")

        with col_vis2:
            st.subheader("Análise de Correlação (Gráfico de Dispersão)")
            indicadores_numericos_scatter = [ind for ind in indicadores_com_dados_ano_pontual if pd.api.types.is_numeric_dtype(df_filtrado_ano_pontual[ind])]
            if len(indicadores_numericos_scatter) >= 2:
                indicador_x_scatter = st.selectbox("Indicador Eixo X (Dispersão):", indicadores_numericos_scatter, index=0, key="scatter_x_pontual_v5") # Chave atualizada
                indicador_y_scatter_opcoes = [ind for ind in indicadores_numericos_scatter if ind != indicador_x_scatter] # Chave atualizada
                if indicador_y_scatter_opcoes:
                    indicador_y_scatter = st.selectbox("Indicador Eixo Y (Dispersão):", indicador_y_scatter_opcoes, index=0 if len(indicador_y_scatter_opcoes) > 0 else -1, key="scatter_y_pontual_v5")# Chave atualizada
                    if indicador_x_scatter and indicador_y_scatter: 
                        df_scatter_valid = df_filtrado_ano_pontual.dropna(subset=[indicador_x_scatter, indicador_y_scatter])
                        if not df_scatter_valid.empty:
                            size_ind_scatter = indicador_x_scatter if indicador_x_scatter in df_scatter_valid.columns and pd.api.types.is_numeric_dtype(df_scatter_valid[indicador_x_scatter]) and (df_scatter_valid[indicador_x_scatter].dropna() > 0).all() else None
                            fig_dispersao = px.scatter(df_scatter_valid, x=indicador_x_scatter, y=indicador_y_scatter, color='País',
                                size=size_ind_scatter, hover_name='País', text='País', title=f"Correlação: {indicador_x_scatter} vs. {indicador_y_scatter} ({ano_selecionado_pontual})")
                            fig_dispersao.update_traces(textposition='top center')
                            st.plotly_chart(fig_dispersao, use_container_width=True)
                        else: st.info(f"Sem dados completos para '{indicador_x_scatter}' vs '{indicador_y_scatter}'.")
                else: st.info("Precisa de pelo menos dois indicadores numéricos diferentes para o eixo Y (dispersão).")
            else: st.info("Sem indicadores numéricos suficientes para gráfico de dispersão.")

    # --- Análise de Desenvolvimento ao Longo do Tempo ---
    st.markdown("---")
    st.header("Análise de Desenvolvimento ao Longo do Tempo")
    
    df_filtrado_series_gerais = df_dados[df_dados['País'].isin(paises_selecionados_gerais)].copy()

    st.subheader("Evolução de Múltiplos Indicadores para um País")
    pais_analise_multi_ind = st.selectbox(
        "Selecione UM País:",
        paises_disponiveis_no_df, 
        index=paises_disponiveis_no_df.index(default_countries[0]) if default_countries and default_countries[0] in paises_disponiveis_no_df else 0,
        key="pais_multi_ind_v5" 
    )
    if pais_analise_multi_ind:
        df_pais_selecionado_multi_ind = df_dados[df_dados['País'] == pais_analise_multi_ind].copy()
        indicadores_pais_multi_ind = [ind for ind in indicadores_disponiveis_df if ind in df_pais_selecionado_multi_ind.columns and df_pais_selecionado_multi_ind[ind].notna().any()]
        
        if indicadores_pais_multi_ind:
            indicadores_plot_multi_ind = st.multiselect(
                "Selecione indicadores para visualizar:",
                indicadores_pais_multi_ind,
                default=indicadores_pais_multi_ind[:min(2, len(indicadores_pais_multi_ind))], 
                key="select_multi_ind_v5" 
            )
            if indicadores_plot_multi_ind:
                df_melted_multi_ind = df_pais_selecionado_multi_ind.melt(
                    id_vars=['País', 'Ano'], value_vars=indicadores_plot_multi_ind,
                    var_name='Indicador', value_name='Valor'
                ).dropna(subset=['Valor'])

                if not df_melted_multi_ind.empty:
                    fig_multi_ind = px.line(df_melted_multi_ind, x='Ano', y='Valor', color='Indicador',
                                            title=f"Evolução de Indicadores para {pais_analise_multi_ind}", markers=True)
                    st.plotly_chart(fig_multi_ind, use_container_width=True)
                else:
                    st.info(f"Nenhum dado válido para os indicadores selecionados para {pais_analise_multi_ind}.")
            else:
                st.info("Selecione pelo menos um indicador.")
        else:
            st.info(f"Nenhum indicador com dados disponível para {pais_analise_multi_ind}.")

    st.markdown("---")
    st.subheader("Série Temporal Comparativa (1 Indicador, Múltiplos Países)")
    indicadores_com_dados_series_gerais = [ind for ind in indicadores_disponiveis_df if ind in df_filtrado_series_gerais.columns and df_filtrado_series_gerais[ind].notna().any()]

    if not paises_selecionados_gerais:
         st.warning("Selecione países no filtro lateral para as visualizações de série temporal comparativa.")
    elif not indicadores_com_dados_series_gerais:
        st.info("Nenhum indicador com dados disponíveis para os países selecionados (série temporal).")
    else:
        indicador_serie_heatmap = st.selectbox(
            "Selecione UM Indicador para Tabela de Série Temporal e Heatmap:",
            indicadores_com_dados_series_gerais,
            key="indicador_heatmap_v5"
        )
        if indicador_serie_heatmap:
            df_serie_filtrada_indicador = df_filtrado_series_gerais[['País', 'Ano', indicador_serie_heatmap]].dropna(subset=[indicador_serie_heatmap])
            if not df_serie_filtrada_indicador.empty:
                df_serie_pivot_table = df_serie_filtrada_indicador.pivot_table(
                    index='País', columns='Ano', values=indicador_serie_heatmap
                ).dropna(how='all', axis=0).dropna(how='all', axis=1)

                st.markdown(f"**Tabela de Série Temporal para: {indicador_serie_heatmap}**")
                if not df_serie_pivot_table.empty:
                    st.dataframe(df_serie_pivot_table.style.format(na_rep="-", precision=2).background_gradient(cmap='RdYlGn', axis=None))
                else:
                    st.info(f"Nenhum dado para '{indicador_serie_heatmap}' para os países selecionados no período após pivotar.")

                st.markdown(f"**Mapa de Calor (Heatmap) para: {indicador_serie_heatmap}**")
                if not df_serie_pivot_table.empty and df_serie_pivot_table.shape[0] > 0 and df_serie_pivot_table.shape[1] > 0:
                    fig_heatmap = px.imshow(
                        df_serie_pivot_table,
                        labels=dict(x="Ano", y="País", color=indicador_serie_heatmap),
                        x=df_serie_pivot_table.columns, y=df_serie_pivot_table.index,
                        text_auto=".2f", aspect="auto", color_continuous_scale=px.colors.diverging.RdYlGn
                    )
                    fig_heatmap.update_xaxes(side="bottom")
                    fig_heatmap.update_layout(title_text=f"Heatmap: {indicador_serie_heatmap} ao longo dos Anos")
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                else:
                    st.info(f"Não há dados suficientes para gerar o heatmap para '{indicador_serie_heatmap}'.")
            else:
                st.info(f"Nenhum dado para '{indicador_serie_heatmap}' para os países selecionados no período.")
        else: 
            st.info("Selecione um indicador para a tabela de série temporal e heatmap.")

    # --- NOVA SEÇÃO: MATRIZ DE CORRELAÇÃO ---
    st.markdown("---")
    st.header(f"Matriz de Correlação entre Indicadores ({ano_selecionado_pontual})")
    st.markdown(f"""
    Esta seção mostra a correlação de Pearson entre os indicadores disponíveis 
    para os **países selecionados na sidebar** e para o **ano {ano_selecionado_pontual} selecionado na sidebar**.
    Valores próximos de 1 indicam forte correlação positiva, próximos de -1 forte correlação negativa, 
    e próximos de 0 pouca correlação linear.
    """)

    if not paises_selecionados_gerais:
        st.warning("Selecione países na sidebar para calcular a matriz de correlação.")
    elif ano_selecionado_pontual is None:
        st.warning("Selecione um ano na sidebar para calcular a matriz de correlação.")
    elif df_filtrado_ano_pontual.empty:
        st.info(f"Nenhum dado disponível para os países selecionados no ano {ano_selecionado_pontual} para calcular correlações.")
    else:
        # Seleciona apenas colunas numéricas dos indicadores disponíveis para correlação
        df_para_corr = df_filtrado_ano_pontual[indicadores_disponiveis_df].copy()
        
        # Remove colunas que são inteiramente NaN para o subconjunto filtrado
        df_para_corr = df_para_corr.dropna(axis=1, how='all')

        # Mantém apenas colunas numéricas
        cols_numericas_corr = [col for col in df_para_corr.columns if pd.api.types.is_numeric_dtype(df_para_corr[col])]
        df_para_corr_numeric = df_para_corr[cols_numericas_corr]

        # Calcula a correlação apenas se houver pelo menos 2 colunas numéricas e 2 linhas (países) com dados não-NaN
        if df_para_corr_numeric.shape[1] >= 2 and df_para_corr_numeric.dropna(how='all').shape[0] >=2 :
            matriz_corr = df_para_corr_numeric.corr()
            
            if not matriz_corr.empty:
                fig_corr_heatmap = px.imshow(
                    matriz_corr,
                    text_auto=".2f", # Mostrar os valores de correlação
                    aspect="auto",
                    color_continuous_scale=px.colors.diverging.RdBu, # Escala de Vermelho-Branco-Azul
                    zmin=-1, zmax=1 # Fixa a escala de cores de -1 a 1
                )
                fig_corr_heatmap.update_layout(
                    title_text=f"Matriz de Correlação dos Indicadores ({ano_selecionado_pontual}, Países: {', '.join(paises_selecionados_gerais)})"
                )
                st.plotly_chart(fig_corr_heatmap, use_container_width=True)
            else:
                st.info("Não foi possível calcular a matriz de correlação (matriz resultante vazia). Verifique os dados.")
        else:
            st.info(f"Não há dados suficientes ou indicadores numéricos suficientes para os países/ano selecionados para calcular uma matriz de correlação (necessário pelo menos 2 indicadores e 2 países com dados). Indicadores numéricos considerados: {', '.join(cols_numericas_corr)}")


    st.markdown("---")
    st.markdown("Dashboard desenvolvido para fins de demonstração para aula de economia.")
    st.markdown("Fontes de dados: Leitura de arquivos CSV locais retirados do Banco Mundial.")