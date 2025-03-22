import streamlit as st
import pandas as pd
import gspread
from datetime import datetime, date
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_gsheets import GSheetsConnection
from dateutil.relativedelta import relativedelta



st.set_page_config(
    page_title="Finanças Analises",
    layout="wide", initial_sidebar_state='collapsed'
)



    
authenticator.login()

st.title('Página de Organização Financeira')

template_dash = "plotly_white"
bg_color_dash = "rgba(0,0,0,0)"




conn = st.connection("gsheets", type=GSheetsConnection)
# Leia os dados da planilha
url_debito = st.secrets["connections"]["gsheets"]["url_extrato_debito"]
url_credito = st.secrets["connections"]["gsheets"]["url_extrato_credito"]
url_extrato_vr = st.secrets["connections"]["gsheets"]["url_extrato_vr"]
url_receitas = st.secrets["connections"]["gsheets"]["url_extrato_receitas"]
url_extrato_fixos =  st.secrets["connections"]["gsheets"]["url_extrato_fixos"]
url_orcamento =  st.secrets["connections"]["gsheets"]["url_orcamento"]
url_investimento = st.secrets["connections"]["gsheets"]["url_investimento"]
url_emprestimos = st.secrets["connections"]["gsheets"]["url_emprestimos"]
url_patriomonio = st.secrets["connections"]["gsheets"]["url_patrimonio"]



debito = conn.read(spreadsheet= url_debito, ttl=360)
credito = conn.read(spreadsheet= url_credito, ttl=360)
receita = conn.read(spreadsheet= url_receitas, ttl=360)
fixo = conn.read(spreadsheet= url_extrato_fixos, ttl=360)
investimento = conn.read(spreadsheet= url_investimento, ttl=360)
emprestimo = conn.read(spreadsheet= url_emprestimos, ttl=360)
vr = conn.read(spreadsheet= url_extrato_vr, ttl=360)
patrimonio = conn.read(spreadsheet= url_patriomonio, ttl=360)
orcamento = conn.read(spreadsheet= url_orcamento, ttl=360)





#agrupando planilhas de gastos mensais
fixo_agrupado = fixo.groupby(['id_mes', 'classificacao'])['valor'].sum().reset_index()
debito_agrupado = debito.groupby(['id_mes'])['valor'].sum().reset_index()
debito_agrupado['classificacao'] = 'Débito'
credito_agrupado = credito.groupby(['id_mes'])['valor'].sum().reset_index()
credito_agrupado_cartao = credito.groupby(['id_mes','credito_cartao'])['valor'].sum().reset_index()
credito_agrupado['classificacao'] = "Crédito"
receita_agrupado = receita.groupby(['id_mes', 'classificacao'])['valor'].sum().reset_index()
patrimonio_agrupado = patrimonio.groupby(['id_mes', 'classificacao'])['valor'].sum().reset_index()
resultado_mensal_agrupado =  pd.concat([fixo_agrupado,debito_agrupado, credito_agrupado, receita_agrupado, patrimonio_agrupado])






# pegando base de orcamento do excel e pegando o real gasto, além disso é feito alguns tratamentos
orcamento_mensal = orcamento
orcamento_mensal_gastos = resultado_mensal_agrupado
orcamento_mensal['id_class'] = orcamento_mensal['id_mes'] + orcamento_mensal['classificacao_orcamento']
orcamento_mensal_gastos['id_class'] = orcamento_mensal_gastos['id_mes'] + orcamento_mensal_gastos['classificacao']
orcamento_unificado = pd.merge(orcamento_mensal, orcamento_mensal_gastos, on='id_class', how='outer')
orcamento_unificado['valor'] = orcamento_unificado['valor'].astype(float) 
orcamento_unificado['Saldo'] = np.where(
        orcamento_unificado['classificacao'].isin(['Renda', 'Juntar']),
        orcamento_unificado['valor'] - orcamento_unificado['valor_orcamento'].astype(float),
        orcamento_unificado['valor_orcamento'].astype(float) - orcamento_unificado['valor'])
orcamento_unificado['Saldo'] = round(orcamento_unificado['Saldo'],2) 

with st.expander('Status Mês atual'):
    orcamento_unificado_debito = orcamento_unificado[orcamento_unificado['classificacao'] == "Débito"]
    orcamento_unificado_debito = orcamento_unificado_debito.sort_values(by='ano')
    
    meses = orcamento_unificado_debito['id_mes_y'].unique().tolist()

    selecione_mes = st.multiselect('Filtre o mês:', meses, default=[meses[-1]])
    




    tipo_receita = receita_agrupado['classificacao'].unique().tolist()
    receitas_orcado =  orcamento_mensal[orcamento_mensal['classificacao_orcamento'].isin(tipo_receita)]
    receitas_orcado.rename(columns={'classificacao_orcamento': 'classificacao'}, inplace=True)
    receitas_real = receita_agrupado
    receitas_real['id_class'] = receitas_real['id_mes'] + receitas_real['classificacao']
    
    visualizacao_renda = st.radio("Escolha a visualização de renda", ['Apenas salário','Todos'])

    if visualizacao_renda == "Apenas salário":
        filtragem_salario = ['Salário','Adiantamento Férias']
        receitas_real = receitas_real[receitas_real['classificacao'].isin(filtragem_salario)]
        receitas_orcado = receitas_orcado[receitas_orcado['classificacao'].isin(filtragem_salario)]
    else:
        receitas_real =receitas_real
        receitas_orcado = receitas_orcado

    

    tipo_fixo = fixo_agrupado['classificacao'].unique().tolist()
    gastos_fixos_orcado = orcamento_mensal[orcamento_mensal['classificacao_orcamento'].isin(tipo_fixo)]
    gastos_fixos_orcado.rename(columns={'classificacao_orcamento': 'classificacao'}, inplace=True)
    
    gastos_fixos_real = fixo_agrupado
    gastos_fixos_real['id_class'] = gastos_fixos_real['id_mes'] + gastos_fixos_real['classificacao']




    def calcular_diferencas(real_df, orcado_df):
        df = pd.merge(
            real_df, orcado_df, on="id_class", how="outer", suffixes=("_real", "_orcado")
        )
        df.fillna(0, inplace=True)
        df["Diferença"] = df["valor"] - df["valor_orcamento"]
        return df

    def construir_dre_classificacao(df, classificacao_nome):
        df = df.groupby("classificacao_consolidado").agg({
            "valor": "sum",
            "valor_orcamento": "sum"
        }).reset_index()

        # Calcular a diferença entre 'valor' e 'valor_orcamento'
        df["diferenca"] = df["valor"] - df["valor_orcamento"]
        dre_classificacao = {}
        for _, row in df.iterrows():
            classificacao = row["classificacao_consolidado"]
            dre_classificacao[f"    - {classificacao}"] = {
                "real": row["valor"],
                "orcado": row["valor_orcamento"]
            }
        total_real = df["valor"].sum()
        total_orcado = df["valor_orcamento"].sum()
        dre_classificacao[f"= Total {classificacao_nome}"] = {
            "real": total_real,
            "orcado": total_orcado
        }
        return dre_classificacao

    # Calcula diferenças
    receitas = calcular_diferencas(receitas_real, receitas_orcado)
    gastos_fixos = calcular_diferencas(gastos_fixos_real, gastos_fixos_orcado)

    receitas['id_mes_consolidado'] = receitas.apply( lambda row: row['id_mes_orcado'] if row['id_mes_real'] == 0 else (
                                row['id_mes_real'] if row['id_mes_orcado'] == '0' else row['id_mes_real']
                                    ), axis=1
                                )

    gastos_fixos['id_mes_consolidado'] = gastos_fixos.apply( lambda row: row['id_mes_orcado'] if row['id_mes_real'] == 0 else (
                                    row['id_mes_real'] if row['id_mes_orcado'] == '0' else row['id_mes_real']
                                        ), axis=1
                                    )


    receitas['classificacao_consolidado'] = receitas.apply( lambda row: row['classificacao_orcado'] if row['classificacao_real'] == 0 else (
                                row['id_mes_real'] if row['classificacao_orcado'] == '0' else row['classificacao_real']
                                    ), axis=1
                                )

    gastos_fixos['classificacao_consolidado'] = gastos_fixos.apply( lambda row: row['classificacao_orcado'] if row['classificacao_real'] == 0 else (
                                    row['classificacao_real'] if row['classificacao_orcado'] == '0' else row['classificacao_real']
                                        ), axis=1
                                    )


    
    receitas = receitas[receitas['id_mes_consolidado'].isin(selecione_mes)]
    gastos_fixos = gastos_fixos[gastos_fixos['id_mes_consolidado'].isin(selecione_mes)]

    
    debito_total_filtrado = debito_agrupado[debito_agrupado['id_mes'].isin(selecione_mes)]
    credito_total_filtrado = credito_agrupado[credito_agrupado['id_mes'].isin(selecione_mes)]
    orcamento_mensal_filtrado = orcamento_mensal[orcamento_mensal['id_mes'].isin(selecione_mes)]

    debito_total = debito_total_filtrado['valor'].sum()
    orcamento_mensal_debito = orcamento_mensal_filtrado[orcamento_mensal_filtrado['classificacao_orcamento']== "Débito"]
    debito_orcado = orcamento_mensal_debito['valor_orcamento'].sum()

    
    credito_total = credito_total_filtrado['valor'].sum()
    orcamento_mensal_credito = orcamento_mensal_filtrado[orcamento_mensal_filtrado['classificacao_orcamento']== "Crédito"]
    credito_orcado = orcamento_mensal_credito['valor_orcamento'].sum()

    orcamento_mensal_sobra = orcamento_mensal_filtrado[orcamento_mensal_filtrado['classificacao_orcamento']== "Sobra"]
    orcamento_sobra = orcamento_mensal_sobra['valor_orcamento'].sum()


    # Sobra Final
    sobra_real = receitas["valor"].sum() - (
        gastos_fixos["valor"].sum() + credito_total + debito_total
    )
    sobra_orcado = orcamento_sobra             


    # Monta DRE dinâmico



    gastos_fixos['valor'] = gastos_fixos['valor'] * -1
    gastos_fixos['valor_orcamento'] = gastos_fixos['valor_orcamento'] * -1
    debito_total =debito_total * -1
    debito_orcado =debito_orcado * -1
    credito_total = credito_total * -1
    credito_orcado = credito_orcado  * -1


    dre_receitas = construir_dre_classificacao(receitas, "de receitas")
    dre_gastos_fixos = construir_dre_classificacao(gastos_fixos, "de gastos fixos")

    # Montagem final do DRE
    dre_data = {
        **dre_receitas,
        **dre_gastos_fixos,
        "= Total gastos com crédito":{
            "real": credito_total,
            "orcado": credito_orcado},
        "= Total gastos com débito":{
            "real": debito_total,
            "orcado": debito_orcado},
        "= Sobra Final": {
            "real": sobra_real,
            "orcado": sobra_orcado,
        }
    }

    # HTML e CSS personalizados
    html_template = """
    <style>
        .dre-container {{
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #444;
            padding: 10px;
            background-color: #1e1e1e;
            color: #f5f5f5;
        }}
        .dre-table {{
            font-family: Arial, sans-serif;
            width: 100%;
            border-collapse: collapse;
        }}
        .dre-table th, .dre-table td {{
            text-align: left;
            padding: 10px;
            border: 1px solid #444;
        }}
        .dre-table th {{
            background-color: #333;
            color: #f5f5f5;
            font-size: 1.1rem;
        }}
        .dre-highlight {{
            font-weight: bold;
            background-color: #292929;
            color: #f5f5f5;
        }}
        .dre-indent {{
            padding-left: 20px;
        }}
    </style>

    <div class="dre-container">
        <table class="dre-table">
            <thead>
                <tr>
                    <th>Descrição</th>
                    <th>Real (R$)</th>
                    <th>Orçado (R$)</th>
                    <th>Diferença (R$)</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """

    # Gerar linhas da tabela dinamicamente
    rows = ""
    for descricao, valores in dre_data.items():
        real = valores["real"]
        orcado = valores["orcado"]
        diferenca = real  - orcado  

        if descricao.startswith("="):  # Destacar totais
            rows += f"""
            <tr class="dre-highlight">
                <td>{descricao}</td>
                <td>{real:,.2f}</td>
                <td>{orcado:,.2f}</td>
                <td>{diferenca:,.2f}</td>
            </tr>
            """
        elif descricao.startswith("    "):  # Recuar subtotais
            rows += f"""
            <tr>
                <td class="dre-indent">{descricao.strip()}</td>
                <td>{real:,.2f}</td>
                <td>{orcado:,.2f}</td>
                <td>{diferenca:,.2f}</td>
            </tr>
            """
        else:  # Linhas normais
            rows += f"""
            <tr>
                <td>{descricao}</td>
                <td>{real:,.2f}</td>
                <td>{orcado:,.2f}</td>
                <td>{diferenca:,.2f}</td>
            </tr>
            """




    # Renderizar o HTML no Streamlit
    st.html(html_template.format(rows=rows))



with st.expander('Status Débito'):
    #criacao dos mestricos
            
    selecao_ano_debito = st.multiselect('Filtre o ano:', [2024,2025], default=2025, key='ano-debito')


    debito_orcamento =  orcamento_unificado[orcamento_unificado['classificacao'] == 'Débito']
    debito_orcamento =  debito_orcamento[debito_orcamento['ano'].isin(selecao_ano_debito)]
    

    col1, col2, col3 =  st.columns(3)
    with col1:
        debito_saldo_atual  = debito_orcamento['Saldo'].iloc[-1]
        st.metric(label="Saldo atual", value=f"{round(debito_saldo_atual,2)}") 
    with col2: 
        debito_saldo_ano = debito_orcamento['Saldo'].sum()
        st.metric(label="Saldo anual", value=f"{round(debito_saldo_ano,2)}") 
    with col3:
        debito_media_mensal = debito_orcamento['valor'].mean()
        st.metric(label="Média mensal", value=f"{round(debito_media_mensal,2)}") 


    #primeiro gráfico que traz uma visão geral de gastos
    tipo_grafico = st.radio("Escolha a visualização", ['Saldo','valor'])

    
    graf_debito_mes = px.bar(
        debito_orcamento,
        x= 'id_mes_y',
        y =tipo_grafico,
        text = tipo_grafico,
        template =template_dash,
        color_discrete_sequence = ["#c1e0e0"]
    )
    graf_debito_mes.update_layout(
        showlegend=False,
        xaxis_title='Mês',
        yaxis_title='Saldo',
        plot_bgcolor =bg_color_dash,
        title={
            'text': f"<b> # GASTO MENSAL DÉBITO {tipo_grafico} <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )

    graf_debito_mes.update_yaxes(visible=False,showticklabels=False)
    st.plotly_chart(graf_debito_mes, use_container_width=True)

    #criação do segundo gráfico
    #consultando no bd a base
    debito_ano = debito[debito['ano'].isin(selecao_ano_debito)]
    debito_agrupado_class =  debito_ano.groupby(['id_mes','classificacao'])['valor'].sum().reset_index()
    
    cores = ["#fce7d2","#ffefa9","#f58f9a","#c0a1ae", "#bfd4ad","#000018","#578bc6"]

    #transformando o valor em float ao invés de decimal
        
    debito_agrupado_class['valor'] = debito_agrupado_class['valor'].astype(float)
    
    #criando id_mes "total"
    total_debito = debito_agrupado_class.groupby('classificacao')['valor'].sum().reset_index()
    total_debito['id_mes'] = 'Total'
    total_debito['Percentual'] = (total_debito['valor'] / total_debito['valor'].sum()) * 100
    debito_agrupado_class = pd.concat([debito_agrupado_class, total_debito], ignore_index=True)
    
    #criando coluna de gastos percentuais
    debito_agrupado_class['Percentual'] = (debito_agrupado_class['valor'] / debito_agrupado_class.groupby('id_mes')['valor'].transform('sum')) * 100
    debito_agrupado_class['Percentual'] = debito_agrupado_class['Percentual'].round(2)
    
    #radio para filtrar tipo de visualização

    radio_graf_debito_class = st.radio("Escolha a visualização", ['Percentual','valor',])

    #se o radio for igual a valor o "total" não aparece porque desconsidguraa
    #além disso se o valor for clicado aparece um metric com o gasto médio e filtro de classificação caso seja do interesse ter uma visão de gasto por classificação
    if radio_graf_debito_class == 'valor':
        debito_agrupado_class = debito_agrupado_class[debito_agrupado_class['id_mes'] != 'Total']
        meses_totais =  debito['id_mes'].nunique()


        debito_agrupado_class_unico = debito_agrupado_class['classificacao'].unique()
        selected_classes = st.multiselect('Filtre as classificações:',debito_agrupado_class_unico, list(debito_agrupado_class_unico))
        debito_agrupado_class = debito_agrupado_class[debito_agrupado_class['classificacao'].isin(selected_classes)]
        debito_agrupado_class_media = round(debito_agrupado_class['valor'].sum()/meses_totais,2)
        
        st.metric(label="Média mensal", value=f"{round(debito_agrupado_class_media,2)}") 
        
    else:
        #se o radio for percentual apenas mostra o gráfico
        debito_agrupado_class = debito_agrupado_class
    
    #ajustando a ordem
    ordem_classificacao = ['Necessidade', 'Aplicativo de Transporte', 'Comida', 'Lazer - Comida','Lazer - Corinthians','Lazer - Outros','Outros']  # Exemplo de ordem que você pode ajustar
    debito_agrupado_class['classificacao'] = pd.Categorical(debito_agrupado_class['classificacao'], categories=ordem_classificacao, ordered=True)
    debito_agrupado_class = debito_agrupado_class.sort_values(by=['id_mes', 'classificacao'])
    
    graf_debito_class = px.bar(
        debito_agrupado_class,
        x= 'id_mes',
        y =radio_graf_debito_class,
        text = radio_graf_debito_class,
        color='classificacao',
        template =template_dash,
        color_discrete_sequence = cores,
            category_orders={
                'id_mes': debito_agrupado_class['id_mes'].unique(),
                'classificacao': ordem_classificacao }
    )

    graf_debito_class.update_layout(
        xaxis_title='Mês',
        yaxis_title='valor',
        plot_bgcolor =bg_color_dash,
        title={
            'text': f"<b> # GASTO DÉBITO POR TIPO - {radio_graf_debito_class} <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
    )

    graf_debito_class.update_yaxes(visible=False,showticklabels=False)
    st.plotly_chart(graf_debito_class, use_container_width=True)


    st.title('Base Débito')

    with st.popover('Filtros'):
        filtro_id_mes = st.multiselect('Selecione o mês',debito_ano['id_mes'].unique(),list(debito_ano['id_mes'].unique()))
        debito_filtrado = debito_ano[debito_ano['id_mes'].isin(filtro_id_mes)]
        filtro_class = st.multiselect('Selecione a classificação',debito_filtrado['classificacao'].unique(),list(debito_filtrado['classificacao'].unique()))
        debito_filtrado = debito_filtrado[debito_filtrado['classificacao'].isin(filtro_class)]
    

    
    debito_filtrado_soma  = debito_filtrado['valor'].sum()

    st.metric(label="Valor Total", value=f"{round(debito_filtrado_soma,2)}") 
    debito_filtrado

with st.expander('Status Crédito'):
    #criacao dos mestricos
            
    selecao_ano_credito = st.multiselect('Filtre o ano:', [2024,2025], default=2025, key='ano-credito')
    


    
    credito_orcamento =  orcamento_unificado[orcamento_unificado['classificacao'] == 'Crédito']
    credito_orcamento =  credito_orcamento[credito_orcamento['ano'].isin(selecao_ano_credito)]


    credito_saldo_ano = credito_orcamento['Saldo'].sum()
    st.metric(label="Saldo anual", value=f"{round(credito_saldo_ano,2)}") 

    tipo_grafico = st.radio("Escolha a visualização", ['Saldo','valor'],key ="grafico_credito")

    
    graf_credito_mes = px.bar(
        credito_orcamento,
        x= 'id_mes_y',
        y =tipo_grafico,
        text = tipo_grafico,
        template =template_dash,
        color_discrete_sequence = ["#c1e0e0"]
    )
    graf_credito_mes.update_layout(
        showlegend=False,
        xaxis_title='Mês',
        yaxis_title='Saldo',
        plot_bgcolor =bg_color_dash,
        title={
            'text': f"<b> # GASTO MENSAL CRÉDITO {tipo_grafico} <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )

    graf_credito_mes.update_yaxes(visible=False,showticklabels=False)
    st.plotly_chart(graf_credito_mes, use_container_width=True)


    #criação do segundo gráfico
    credito_ano = credito[credito['ano'].isin(selecao_ano_credito)]
    credito_agrupado_class =  credito_ano.groupby(['id_mes','classificacao'])['valor'].sum().reset_index()
    
    cores = ["#fce7d2","#ffefa9","#f58f9a","#c0a1ae", "#bfd4ad","#000018","#578bc6"]

    #transformando o valor em float ao invés de decimal
        
    credito_agrupado_class['valor'] = credito_agrupado_class['valor'].astype(float)
    
    #criando id_mes "total"
    total_credito = credito_agrupado_class.groupby('classificacao')['valor'].sum().reset_index()
    total_credito['id_mes'] = 'Total'
    total_credito['Percentual'] = (total_credito['valor'] / total_credito['valor'].sum()) * 100
    credito_agrupado_class = pd.concat([credito_agrupado_class, total_credito], ignore_index=True)
    
    #criando coluna de gastos percentuais
    credito_agrupado_class['Percentual'] = (credito_agrupado_class['valor'] / credito_agrupado_class.groupby('id_mes')['valor'].transform('sum')) * 100
    credito_agrupado_class['Percentual'] = credito_agrupado_class['Percentual'].round(2)

    radio_graf_credito_class = st.radio("Escolha a visualização", ['Percentual','valor'], key='radio_grafico_class_credito')

    #se o radio for igual a valor o "total" não aparece porque desconsidguraa
    #além disso se o valor for clicado aparece um metric com o gasto médio e filtro de classificação caso seja do interesse ter uma visão de gasto por classificação
    if radio_graf_credito_class == 'valor':
        credito_agrupado_class = credito_agrupado_class[credito_agrupado_class['id_mes'] != 'Total']
        meses_totais =  credito['id_mes'].nunique()


        credito_agrupado_class_unico = credito_agrupado_class['classificacao'].unique()
        selected_classes = st.multiselect('Filtre as classificações:',credito_agrupado_class_unico, list(credito_agrupado_class_unico))
        credito_agrupado_class = credito_agrupado_class[credito_agrupado_class['classificacao'].isin(selected_classes)]
        credito_agrupado_class_media = round(credito_agrupado_class['valor'].sum()/meses_totais,2)
        
        st.metric(label="Média mensal", value=f"{round(credito_agrupado_class_media,2)}") 
        
    else:
        #se o radio for percentual apenas mostra o gráfico
        credito_agrupado_class = credito_agrupado_class

    ordem_classificacao_credito = ['Presente Pitica', 'Roupas', 'Compras Minhas', 'Outros','Presentes - Família','Juros/Anuidade','Faturas 2023']  # Exemplo de ordem que você pode ajustar
    credito_agrupado_class['classificacao'] = pd.Categorical(credito_agrupado_class['classificacao'], categories=ordem_classificacao_credito, ordered=True)
    credito_agrupado_class = credito_agrupado_class.sort_values(by=['id_mes', 'classificacao'])
    
    graf_credito_class = px.bar(
        credito_agrupado_class,
        x= 'id_mes',
        y =radio_graf_credito_class,
        text = radio_graf_credito_class,
        color='classificacao',
        template =template_dash,
        color_discrete_sequence = cores,
            category_orders={
                'id_mes': credito_agrupado_class['id_mes'].unique(),
                'classificacao': ordem_classificacao_credito }
    )

    graf_credito_class.update_layout(
        xaxis_title='Mês',
        yaxis_title='valor',
        plot_bgcolor =bg_color_dash,
        title={
            'text': f"<b> # GASTO CRÉDITO POR TIPO - {radio_graf_credito_class} <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
    )

    graf_credito_class.update_yaxes(visible=False,showticklabels=False)
    st.plotly_chart(graf_credito_class, use_container_width=True)

    st.title('Base Crédito')

    with st.popover('Filtros'):
        filtro_id_mes_credito = st.multiselect('Selecione o mês',credito_ano['id_mes'].unique(),list(credito_ano['id_mes'].unique()), key='filtro_idmes_credito')
        credito_filtrado = credito_ano[credito_ano['id_mes'].isin(filtro_id_mes_credito)]
        filtro_class_credito = st.multiselect('Selecione a classificação',credito_filtrado['classificacao'].unique(),list(credito_filtrado['classificacao'].unique()))
        credito_filtrado = credito_filtrado[credito_filtrado['classificacao'].isin(filtro_class_credito)]
        filtro_credito_cartao = st.multiselect('Selecione o cartão',credito_filtrado['credito_cartao'].unique(),list(credito_filtrado['credito_cartao'].unique()))
        credito_filtrado = credito_filtrado[credito_filtrado['credito_cartao'].isin(filtro_credito_cartao)]
    

            
    credito_filtrado_soma  = credito_filtrado['valor'].sum()

    st.metric(label="Valor Total", value=f"{round(credito_filtrado_soma,2)}") 
    credito_filtrado

with st.expander('Status Patrimônio'):
    
    patrimonio_sem_reservas = patrimonio[patrimonio['direcionamento'] == "Patrimônio"]
    total_patrimonio_sem_reservas =  round(patrimonio_sem_reservas['valor'].sum(),2)

    
    total_emprestimo = round(emprestimo['valor'].sum(),2)
    total_investimento = round(investimento['valor'].sum(),2)
    valor_em_maos = total_patrimonio_sem_reservas - total_emprestimo - total_investimento
    patrimonio_agrupado = patrimonio.groupby(['direcionamento'])['valor'].sum().reset_index()

    novas_linhas = pd.DataFrame({ 'direcionamento': ['Valor em mãos','Empréstimo', 'Investimento'], 'valor': [valor_em_maos,total_emprestimo, total_investimento]})
    patrimonio_agrupado = pd.concat([patrimonio_agrupado, novas_linhas], ignore_index=True)
    patrimonio_agrupado = patrimonio_agrupado[patrimonio_agrupado['direcionamento'] != 'Patrimônio']
    patrimonio_agrupado['percentual'] = (patrimonio_agrupado['valor'] / patrimonio_sem_reservas['valor'].sum() * 100).round(2)

    
    col1,col2 = st.columns(2)
    with col1:
        patrimonio_total  = patrimonio['valor'].sum()
        st.metric(label="Patrimônio total", value=patrimonio_total) 
    with col2:
        patrimonio_total_sem_reservas  = patrimonio_sem_reservas['valor'].sum()
        st.metric(label="Patrimônio total - Sem reservas", value=patrimonio_total_sem_reservas) 

    


    tipo_visualizacao_patrimonio1 = st.radio("Selecione a visualização:", ["valor","percentual"])

    graf_patrimonio_quebrado = px.bar(
        patrimonio_agrupado,
        x='direcionamento',
        y=tipo_visualizacao_patrimonio1,
        text=tipo_visualizacao_patrimonio1,
        template=template_dash,  # Pode ajustar o template ao seu gosto
        color_discrete_sequence=["#c1e0e0"]
    )

    graf_patrimonio_quebrado.update_layout(
        showlegend=False,
        xaxis_title='Mês',
        yaxis_title=tipo_visualizacao_patrimonio1,
        plot_bgcolor=bg_color_dash,
        title={
            'text': f"<b> Distribuição patrimônio - {tipo_visualizacao_patrimonio1} <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    graf_patrimonio_quebrado.update_yaxes(visible=False, showticklabels=False)
    st.plotly_chart(graf_patrimonio_quebrado, use_container_width=True)

    patrimonio_agrupado_mes = patrimonio_sem_reservas.groupby(['id_mes','ano'])['valor'].sum().reset_index()

    selecao_ano_patrimonio = st.multiselect('Filtre o ano:', [2024,2025], default=2025, key='ano-patrimonio')


    patrimonio_agrupado_mes =  patrimonio_agrupado_mes[patrimonio_agrupado_mes['ano'].isin(selecao_ano_patrimonio)]

    tipo_visualizacao_patrimonio2 = st.radio("Selecione a visualização:", ["Acumulado","Arrecadado por mês"])
    # Lógica para acumulado
    if tipo_visualizacao_patrimonio2 == "Acumulado":
        patrimonio_agrupado_mes['valor'] = patrimonio_agrupado_mes['valor'].cumsum()

    # Criar o gráfico
    graf_patrimonio = px.bar(
        patrimonio_agrupado_mes,
        x='id_mes',
        y='valor',
        text='valor',
        template=template_dash,  # Pode ajustar o template ao seu gosto
        color_discrete_sequence=["#c1e0e0"]
    )

    graf_patrimonio.update_layout(
        showlegend=False,
        xaxis_title='Mês',
        yaxis_title='Patrimônio total' if tipo_visualizacao_patrimonio2 == "Acumulado" else 'Arrecadado por mês',
        plot_bgcolor=bg_color_dash,
        title={
            'text': f"<b> {'# PATRIMÔNIO ACUMULADO' if tipo_visualizacao_patrimonio2 == 'Acumulado' else '# ARRECADADO POR MÊS'} <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    graf_patrimonio.update_yaxes(visible=False, showticklabels=False)
    st.plotly_chart(graf_patrimonio, use_container_width=True)


    with st.popover('Filtros'):
        selecao_ano_patrimonio2 = st.multiselect('Selecione o ano',patrimonio['ano'].unique(),list(patrimonio['ano'].unique()), key='filtro_idmes_patrimonio-2')
        patrimonio_filtrado = patrimonio[patrimonio['ano'].isin(selecao_ano_patrimonio2)]

        filtro_id_mes_patrimonio = st.multiselect('Selecione o mês',patrimonio['id_mes'].unique(),list(patrimonio['id_mes'].unique()), key='filtro_idmes_patrimonio')
        patrimonio_filtrado = patrimonio_filtrado[patrimonio_filtrado['id_mes'].isin(filtro_id_mes_patrimonio)]

        filtro_direcionamento_patrimonio = st.multiselect('Selecione o direcionamento',patrimonio_filtrado['direcionamento'].unique(),list(patrimonio_filtrado['direcionamento'].unique()))
        patrimonio_filtrado = patrimonio_filtrado[patrimonio_filtrado['direcionamento'].isin(filtro_direcionamento_patrimonio)]

        filtro_classificacao_patrimonio = st.multiselect('Selecione a classificação',patrimonio_filtrado['classificacao'].unique(),list(patrimonio_filtrado['classificacao'].unique()))
        patrimonio_filtrado = patrimonio_filtrado[patrimonio_filtrado['classificacao'].isin(filtro_classificacao_patrimonio)]


    patrimonio_filtrado_soma  = patrimonio_filtrado['valor'].sum()

    st.metric(label="Valor Total", value=f"{round(patrimonio_filtrado_soma,2)}") 
    patrimonio_filtrado

with st.expander('Status Emprestimos'):
    

    emprestimo = emprestimo[emprestimo['emprestimo_destinatario'] != 'Pai']
    valor_total_emprestado = round(emprestimo['valor'].sum(),2) 
    st.metric(label="Valor total emprestado", value=valor_total_emprestado)
    emprestimo_agrupado_destinatario =  emprestimo.groupby('emprestimo_destinatario')['valor'].sum().reset_index()
    emprestimo_agrupado_destinatario = emprestimo_agrupado_destinatario[emprestimo_agrupado_destinatario['valor'] != 0]

    
    graf_emprestimo = px.bar(
        emprestimo_agrupado_destinatario,
        x= 'emprestimo_destinatario',
        y ='valor',
        text = 'valor',
        template =template_dash,
        color_discrete_sequence = ["#c1e0e0"]
    )
    graf_emprestimo.update_layout(
        showlegend=False,
        xaxis_title='Pessoa',
        yaxis_title='Valor total',
        plot_bgcolor =bg_color_dash,
        title={
            'text': "<b> # VALOR EMPRESTADO POR PESSOA <b>",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )

    graf_emprestimo.update_yaxes(visible=False,showticklabels=False)
    st.plotly_chart(graf_emprestimo, use_container_width=True)


    filtro_emprestimo = st.multiselect('Selecione a pessoa',emprestimo['emprestimo_destinatario'].unique(),list(emprestimo['emprestimo_destinatario'].unique()))
    emprestimo_filtrado = emprestimo[emprestimo['emprestimo_destinatario'].isin(filtro_emprestimo)]

    emprestimo_filtrado


with st.expander('Status Investimentos'):

    valor_total_investido = round(investimento['valor'].sum(),2) 
    st.metric(label="Valor total investido", value=valor_total_investido)
    investimento
