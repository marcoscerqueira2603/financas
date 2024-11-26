import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from openpyxl import load_workbook
import gspread
from google.auth import exceptions
from google.auth.transport.requests import Request
from datetime import datetime, date
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from dateutil.relativedelta import relativedelta
from sqlalchemy import text

st.set_page_config(
    page_title="Finanças",
    layout="wide"
)

st.title('Página de Organização Financeira')

template_dash = "plotly_white"
bg_color_dash = "rgba(0,0,0,0)"

load_dotenv()

# Configuração da conexão
conn = st.connection("postgresql", type="sql")

def consultar_db(query):
    """
    Consulta ao banco de dados usando st.connection.
    Retorna um DataFrame com os resultados.
    """
    try:
        # Realiza a consulta e retorna um DataFrame
        df = conn.query(query, ttl="10m")  # Cache de 10 minutos
        return df

    except Exception as e:
        st.write(f"Erro ao consultar o banco de dados: {e}")
        return None

# Função para adicionar dados




tab1, tab2 = st.tabs(['Adicionar dados','Visualização'])

with tab1:

    with st.expander('Débito'):
        st.title('Débito')

        #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição
        novos_debitos = []


        with st.form('form débito'):
            # Campos para inserir as informações do débito
            debito_mes_ref = st.selectbox('Selecione o mês referência:', 
                                        ['01_2024','02_2024','03_2024','04_2024','05_2024','06_2024','07_2024',
                                        '08_2024','09_2024','10_2024','11_2024','12_2024'], key='class-mesref_debito')

            debito_data = st.text_input('Insirir Data', key="inserir-data-debito")
            debito_descricao = st.text_input('Insirir Descrição', key="inserir-descricao-debito")

            debito_classificacao = st.selectbox('Selecione o tipo:', 
                                            ['Necessidade', 'Lazer - Corinthians', 'Lazer - Outros', 'Lazer - Comida', 
                                                'Comida', 'Aplicativo de Transporte', 'Outros'], key='class-debito')

            debito_valor = st.text_input('Insirir Valor', key="inserir-valor-debito")
            debito_compracredito = st.selectbox('Selecione o tipo:', 
                                            ['Não', 'Sim, com pagamento', 'Sim, sem pagamento'], key='compra-credito-debito')

            # Verificação de valor (caso esteja vazio, coloca 1.0 como padrão)
            if debito_valor == "":
                debito_valor = 1.0
            else:
                debito_valor = float(debito_valor)

            # Definindo data padrão caso o campo esteja vazio
            if debito_data == "":
                debito_data = "08/02/2000"
            
            # Botão de envio do formulário
            submit_button = st.form_submit_button("Adicionar Débito")

            if submit_button:
                with conn.session as session:
                    # Declarar a query como um texto SQL explícito
                    query = text("""
                        INSERT INTO financas.debito
                        (id_mes, data, classificacao, descricao, debito_compra_credito, valor)
                        VALUES (:id_mes, :data, :classificacao, :descricao, :debito_compra_credito, :valor);
                    """)
                    # Executar a query
                    session.execute(query, {
                        "id_mes": debito_mes_ref,
                        "data": debito_data,
                        "classificacao": debito_classificacao,
                        "descricao": debito_descricao,
                        "debito_compra_credito": debito_compracredito,
                        "valor": debito_valor
                    })
                    # Confirmar as alterações
                    session.commit()
                    st.success("Débito adicionado com sucesso!")

                # Adiciona o novo débito à lista de débitos
                novo_debito = [debito_mes_ref, debito_data, debito_classificacao, debito_descricao, debito_compracredito, debito_valor]
                novos_debitos.append(novo_debito)





with tab2:

    # pegando base de orcamento do excel e pegando o real gasto, além disso é feito alguns tratamentos
    orcamento_mensal_gastos = consultar_db("select * from financas.orcamento_mes")
    orcamento_mensal['id_class'] = orcamento_mensal['id_mes'] + orcamento_mensal['classificacao_orcamento']
    orcamento_mensal_gastos['id_class'] = orcamento_mensal_gastos['id_mes'] + orcamento_mensal_gastos['classificacao']
    orcamento_unificado = pd.merge(orcamento_mensal, orcamento_mensal_gastos, on='id_class', how='outer')
    orcamento_unificado['valor'] = orcamento_unificado['valor'].astype(float) 
    orcamento_unificado['Saldo'] = np.where(
    orcamento_unificado['classificacao'].isin(['Renda', 'Juntar']),
    orcamento_unificado['valor'] - orcamento_unificado['valor_orcamento'].astype(float),
    orcamento_unificado['valor_orcamento'].astype(float) - orcamento_unificado['valor'])
    orcamento_unificado['Saldo'] = round(orcamento_unificado['Saldo'],2) 

    with st.expander('Status Débito'):
        #criacao dos mestricos
        debito_orcamento =  orcamento_unificado[orcamento_unificado['classificacao'] == 'Débito']
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
        debito_agrupado_class =  consultar_db("SELECT id_mes, classificacao, SUM(valor) AS valor FROM financas.debito GROUP BY id_mes, classificacao ORDER BY id_mes, classificacao")
        
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
            meses_totais = consultar_db("SELECT COUNT(DISTINCT id_mes) AS total_id_mes FROM financas.debito")
            meses_totais = meses_totais['total_id_mes'].iloc[0]

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
            debito_bd = consultar_db("select * from financas.debito") 
            filtro_id_mes = st.multiselect('Selecione o mês',debito_bd['id_mes'].unique(),list(debito_bd['id_mes'].unique()))
            debito_filtrado = debito[debito_bd['id_mes'].isin(filtro_id_mes)]
            filtro_class = st.multiselect('Selecione a classificação',debito_filtrado['classificacao'].unique(),list(debito_filtrado['classificacao'].unique()))
            debito_filtrado = debito_filtrado[debito_filtrado['classificacao'].isin(filtro_class)]
        debito_filtrado

     
    
