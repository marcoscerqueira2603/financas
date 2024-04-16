from calendar import c
import streamlit as st
import pandas as pd
import os
from openpyxl import load_workbook
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.stats import poisson


st.set_page_config(
    page_title="Finanças",
    layout="wide"
)


st.title('Página de Organização Financeira')

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("chave_api.json", scope)
client = gspread.authorize(creds)


@st.cache_data(ttl=20)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

debito = load_data(st.secrets["url_extrato_debito"])

@st.cache_data(ttl=20)
def load_data2(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

credito = load_data2(st.secrets["url_extrato_credito"])

@st.cache_data(ttl=20)
def load_data3(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

vr = load_data3(st.secrets["url_extrato_vr"])

@st.cache_data(ttl=20)
def load_data4(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

receita = load_data4(st.secrets["url_extrato_receitas"])

@st.cache_data(ttl=20)
def load_data5(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

fixos = load_data5(st.secrets["url_extrato_fixos"])

@st.cache_data(ttl=20)
def load_data6(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

orcamento_mensal = load_data6(st.secrets["url_orcamento_mensal"])


tab1,tab2,tab3, tab4, tab5,tab6, tab7 = st.tabs(['Incluir Dados', 'Status Mês Atual', 'Análises Débitos','Análises Créditos','Análises VR','Análises Fixos','Patrimônio'])

with tab1:   
    with st.expander('Débito'):
        st.title('Débito')

        #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição

        #a partir do calculo de data conseguimos ter o mes e jogamos lá
        debito_mes_ref = st.selectbox('Selecione o mês referência:', ['1 - janeiro', '2 - fevereiro', '3 - março', '4 - abril', '5 - maio','6 - junho', '7 - julho','8 - agosto','9 - setembro','10 - outubro','11 - novembro','12 - dezembro'], key='class-mesref_debito')
        debito_data = st.text_input('Insirir Data', key = "inserir-data-debito")
        debito_descrição =  st.text_input('Insirir Descrição', key = "inserir-descricao-debito")

        debito_classificacao = st.selectbox('Selecione o tipo:', ['Necessidade', 'Lazer - Corinthians', 'Lazer - Outros', 'Lazer - Comida', 'Comida','Aplicativo de Transporte', 'Outros' ], key='class-debito')
        debito_valor = st.text_input('Insirir Valor', key = "inserir-valor-debito")

        if debito_valor == "":
            debito_valor = 1.0
        else:
            debito_valor = debito_valor

        debito_valor = float(debito_valor)

        if debito_data  == "":
            debito_data = "08/02/2000"
        else:
            debito_data = debito_data    


        novos_debitos = []

        with st.form('form débito'):
            if st.form_submit_button('Adicionar Débito'):
                novo_debito = [debito_data, debito_mes_ref,  debito_descrição, debito_classificacao, debito_valor]
                novos_debitos.append(novo_debito)

        if novos_debitos:
            novos_debitos_df = pd.DataFrame(novos_debitos, columns=debito.columns)
            worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lEIcy7vjH-X7U1t-toxC6V-ps39f6WQw2mruzTfx1VE/edit#gid=0').get_worksheet(0)
            
            # Obter o número de linhas existentes na planilha
            num_rows = len(worksheet.get_all_values())
            
            # Inserir os dados nas linhas subsequentes
            values_to_insert = novos_debitos_df.values.tolist()
            worksheet.insert_rows(values_to_insert, num_rows + 1) 

    with st.expander('VR'):
            st.title('VR')

            #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição

            #a partir do calculo de data conseguimos ter o mes e jogamos lá
            vr_mes_ref = st.selectbox('Selecione o mês referência:', ['1 - janeiro', '2 - fevereiro', '3 - março', '4 - abril', '5 - maio','6 - junho', '7 - julho','8 - agosto','9 - setembro','10 - outubro','11 - novembro','12 - dezembro'], key='class-mesref_vr')
            vr_data = st.text_input('Insirir Data',key = 'insirir-data-vr')
            vr_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-vr')
            vr_local =  st.text_input('Insirir Local', key = 'insirir-local-vr')
            vr_classificacao = st.selectbox('Selecione o tipo:', ['Almoço no escritório','Saídas','Saídas - Pitica','Rua','Casa','Outros'], key='class-vr')
            vr_valor = st.text_input('Insirir Valor', key = 'insirir-valor-vr')

            if vr_valor == "":
                vr_valor = 1.0
            else:
                vr_valor = vr_valor

            vr_valor = float(vr_valor)

            if vr_data  == "":
                vr_data = "08/02/2000"
            else:
                vr_data = vr_data    


            novos_vrs = []

            with st.form('form vr'):
                if st.form_submit_button('Adicionar Gastor VR'):
                    novo_vr = [ vr_data, vr_mes_ref, vr_descrição,vr_local,  vr_classificacao, vr_valor]
                    novos_vrs.append(novo_vr)

            if novos_vrs:
                novos_vrs_df = pd.DataFrame(novos_vrs, columns=vr.columns)
                worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1ZCMCzyrMdzIDkGnNZAErAyowwi8FzkivIFWhwEDyII8/edit#gid=0').get_worksheet(0)
                
                # Obter o número de linhas existentes na planilha
                num_rows = len(worksheet.get_all_values())
                
                # Inserir os dados nas linhas subsequentes
                values_to_insert = novos_vrs_df.values.tolist()
                worksheet.insert_rows(values_to_insert, num_rows + 1) 
                vr

    with st.expander('Crédito'):
    
        st.title('Crédito')

        credito_parcelas =  st.number_input('Inserir Parcelas', value=1)
        credito_mes_parcela1 =  st.number_input('Inserir Mês 1ª Parcela', value=1)
        credito_valor = st.text_input('Insirir Valor Crédito', key = 'insirir-valor-credito')
        credito_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-credito')
        credito_classificacao = st.selectbox('Selecione o tipo:', ['Faturas 2023','Presente Pitica','Presentes - Família','Lazer','Roupas','Compras Minhas','Outros'], key='class-credito')
        credito_cartao = st.selectbox('Selecione o cartão:', ['Inter','Nubank','C6','Renner'], key='cartao-credito')


        if credito_valor == "":
            credito_valor = 100.0
        else:
            credito_valor = credito_valor

        credito_valor = float(credito_valor)

        credito_valor_parcela = round(credito_valor/credito_parcelas,2)
        novos_creditos = []
        
        with st.form('form credito'):
            if st.form_submit_button('Adicionar Gasto Crédito'):
                for i in range(credito_parcelas):
                    novo_credito = [credito_mes_parcela1, credito_descrição, credito_classificacao,  credito_cartao, credito_valor_parcela]
                    novos_creditos.append(novo_credito)
                    credito_mes_parcela1  = credito_mes_parcela1+1

        if novos_creditos:
            novos_creditos_df = pd.DataFrame(novos_creditos, columns=credito.columns)
            worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1xU7NwhHQkMGcF742y-tj9MjuK7XYnNhVt9r8dV60ofc/edit#gid=0').get_worksheet(0)
            
            # Obter o número de linhas existentes na planilha
            num_rows = len(worksheet.get_all_values())
            
            # Inserir os dados nas linhas subsequentes
            values_to_insert = novos_creditos_df.values.tolist()
            worksheet.insert_rows(values_to_insert, num_rows + 1) 
            
    with st.expander("Receita"): 
        st.title("Receita")
        
        receita_data = st.text_input('Insirir Data',key = 'insirir-data-receita ')
        receita_mes_ref = st.selectbox('Selecione o mês referência:', ['1 - janeiro', '2 - fevereiro', '3 - março', '4 - abril', '5 - maio','6 - junho', '7 - julho','8 - agosto','9 - setembro','10 - outubro','11 - novembro','12 - dezembro'], key='class-mesref_reeitas')
        if receita_data  == "":
            receita_data = "08/02/2000"
        else:
            receita_data = receita_data    

      
        receita_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-receita')
        receita_classificacao = st.selectbox('Selecione o tipo:', ['Salário','VR','Bônus','13º','VR','Cartola','Apostas','Investimentos'], key='class-receita')

        receita_valor = st.text_input('Insirir Valor', key = 'insirir-valor-receita')

        if receita_valor == "":
            receita_valor = 1.0
        else:
            receita_valor = receita_valor

        receita_valor = float(receita_valor)

        novos_receitas = []

        with st.form('form receita'):
            if st.form_submit_button('Adicionar Receitas'):
                novo_receita = [receita_data, receita_mes_ref, receita_descrição, receita_classificacao, receita_valor]
                novos_receitas.append(novo_receita)

        if novos_receitas:
            novos_receitas_df = pd.DataFrame(novos_receitas, columns=receita.columns)
            worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/11diab8Ytz3q9wN_ZbxWw60DBH5ydBUb152pIhmC0Etw/edit#gid=0').get_worksheet(0)
            
            # Obter o número de linhas existentes na planilha
            num_rows = len(worksheet.get_all_values())
            
            # Inserir os dados nas linhas subsequentes
            values_to_insert = novos_receitas_df.values.tolist()
            worksheet.insert_rows(values_to_insert, num_rows + 1) 
            

    with st.expander('Fixos'):
        st.title('Fixos')

        fixos_mes_ref = st.selectbox('Selecione o mês referência:', ['1 - janeiro', '2 - fevereiro', '3 - março', '4 - abril', '5 - maio','6 - junho', '7 - julho','8 - agosto','9 - setembro','10 - outubro','11 - novembro','12 - dezembro'], key='class-mesref_fixos')
        fixos_data = st.text_input('Insirir Data', key = "inserir-data-fixos")
        fixos_descrição =  st.text_input('Insirir Descrição', key = "inserir-descricao-fixos")

        fixos_classificacao = st.selectbox('Selecione o tipo:', ['Casa', 'Fiel Torcedor', 'Cabelo', 'Internet Celular', 'Spotify','Passagem', 'Seguro Celular','Streaming','Tembici - Itaú',], key='class-fixos')
        fixos_valor = st.text_input('Insirir Valor', key = "inserir-valor-fixos")

        if fixos_valor == "":
            fixos_valor = 1.0
        else:
            fixos_valor = fixos_valor

        fixos_valor = float(fixos_valor)

        if fixos_data  == "":
            fixos_data = "08/02/2000"
        else:
            fixos_data = fixos_data    

        fixos_algumcredito =  st.selectbox('Gasto em algum crédito?:', ['-', 'Nubank','Crédito' ], key='class-algumcredito_fixos')

        novos_fixos = []
        with st.form('form fixos'):
            if st.form_submit_button('Adicionar Fixos'):
                novos_fixo = [fixos_data, fixos_mes_ref,  fixos_descrição, fixos_classificacao,fixos_algumcredito, fixos_valor]
                novos_fixos.append(novos_fixo)
        
        if novos_fixos:
            novos_fixos_df = pd.DataFrame(novos_fixos, columns=fixos.columns)
            worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1AxG0j2qOZ9e1MRUCD20Jhd0roqPcZ8lcQPBhlIqwwGs/edit#gid=0').get_worksheet(0)
            
            # Obter o número de linhas existentes na planilha
            num_rows = len(worksheet.get_all_values())
            
            # Inserir os dados nas linhas subsequentes
            values_to_insert = novos_fixos_df.values.tolist()
            worksheet.insert_rows(values_to_insert, num_rows + 1) 

    with st.expander('Orçamento Mês'):
        st.title('Orçamento do mês')
        orcamentos_classificacao = st.selectbox('Selecione o tipo:', ['Salário', 'Casa', 'Fiel Torcedor', 'Cabelo', 'Internet Celular', 'Spotify','Passagem', 'Seguro Celular','Streaming','Tembici - Itaú','Crédito - Nubank', 'Crédito - Inter','Crédito - Renner','Débito', 'Juntar','Crédito', 'VR'], key='class-orcamentos')
       
        orcamentos_mes_ref = st.selectbox('Selecione o mês referência:', ['1 - janeiro', '2 - fevereiro', '3 - março', '4 - abril', '5 - maio','6 - junho', '7 - julho','8 - agosto','9 - setembro','10 - outubro','11 - novembro','12 - dezembro'], key='class-orcamento')

        orcamentos_valor = st.text_input('Insirir Valor', key = "inserir-valor-orcamentos")

        if orcamentos_valor== "":
            orcamentos_valor = 1.0
        else:
            orcamentos_valor = orcamentos_valor

        orcamentos_valor = float(orcamentos_valor)

        novos_orcamentos_mensais = []

        with st.form('form orcamento mensais'):
            if st.form_submit_button('Adicionar Orçamento'):
                novo_orcamentos_mensais = [orcamentos_mes_ref, orcamentos_classificacao,orcamentos_valor ]
                novos_orcamentos_mensais.append(novo_orcamentos_mensais)

        if novos_orcamentos_mensais:
            novos_orcamentos_mensais_df = pd.DataFrame(novos_orcamentos_mensais, columns=orcamento_mensal.columns)
            worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1D1lU2R55OpfwdA8INDPdan3VGM-3oZ56BRYiSr2uCvE/edit#gid=0').get_worksheet(0)
            
            # Obter o número de linhas existentes na planilha
            num_rows = len(worksheet.get_all_values())
            
            # Inserir os dados nas linhas subsequentes
            values_to_insert = novos_orcamentos_mensais_df.values.tolist()
            worksheet.insert_rows(values_to_insert, num_rows + 1)                 

        orcamento_mensal_credito = orcamento_mensal[orcamento_mensal['Tipo Orçamento'] == "Crédito"]
        orcamento_mensal_vr = orcamento_mensal[orcamento_mensal['Tipo Orçamento'] == "VR"]
        orcamento_mensal =  orcamento_mensal[(orcamento_mensal['Tipo Orçamento'] != "Crédito") &(orcamento_mensal['Tipo Orçamento'] != "VR")]

        orcamento_mensal_salario = orcamento_mensal[orcamento_mensal['Tipo Orçamento'] == 'Salário'] 
        orcamento_mensal_sem_salario = orcamento_mensal[orcamento_mensal['Tipo Orçamento'] != 'Salário']
        orcamento_mensal_sem_salario = orcamento_mensal_sem_salario[orcamento_mensal_sem_salario['Tipo Orçamento'] != 'Patrimonio que sobrou de 2023']
        orcamento_mensal_sem_salario = orcamento_mensal_sem_salario.drop('Tipo Orçamento', axis=1)
        orcamento_mensal_salario = orcamento_mensal_salario.drop('Tipo Orçamento', axis=1)
        orcamento_mensal_salario = orcamento_mensal_salario.reset_index(drop=True)
        orcamento_mensal_salario.set_index('Mês', inplace=True)
        orcamento_mensal_salario['Valor'] = orcamento_mensal_salario['Valor'].str.replace('.','').str.replace(',','.')
        orcamento_mensal_salario['Valor'] = orcamento_mensal_salario['Valor'].astype(float)

        orcamento_mensal_sem_salario = orcamento_mensal_sem_salario.rename(columns={'Valor':'Valor_2'} )
        orcamento_mensal_sem_salario['Valor_2'] = orcamento_mensal_sem_salario['Valor_2'].str.replace('.','').str.replace(',','.')
        orcamento_mensal_sem_salario['Valor_2'] = orcamento_mensal_sem_salario['Valor_2'].astype(float)
        orcamento_mensal_sem_salario = orcamento_mensal_sem_salario.groupby('Mês')['Valor_2'].sum()
        
        orcamento_mensal_consolidado = pd.merge(orcamento_mensal_salario, orcamento_mensal_sem_salario, on='Mês', how='outer')
        orcamento_mensal_consolidado['Sobra'] =  orcamento_mensal_consolidado['Valor'] -  orcamento_mensal_consolidado['Valor_2']
        orcamento_mensal_consolidado

with tab3:

    st.title("Análises Débitos")

    debito['Valor'] = debito['Valor'].str.replace(',', '.')
    debito['Valor'] = debito['Valor'].astype(float)
    debito_mes  = debito.groupby(['Mês Referência'])['Valor'].sum()
    orcamento_mensal_debito = orcamento_mensal[orcamento_mensal['Tipo Orçamento'] == "Débito"]
    orcamento_mensal_debito =  orcamento_mensal_debito.rename(columns={'Mês': 'Mês Referência', 'Valor':'Valor_Orcamento'})

    debito_mes_consolidado =  pd.merge(debito_mes,orcamento_mensal_debito, on='Mês Referência',how='outer' )
    debito_mes_consolidado['Valor_Orcamento'] = debito_mes_consolidado['Valor_Orcamento'].str.replace(',','.')
    debito_mes_consolidado['Valor'] = round(debito_mes_consolidado['Valor'],2)
    debito_mes_consolidado['Valor_Orcamento'] = round(debito_mes_consolidado['Valor_Orcamento'],2)

    grafico_debito =  go.Figure()

    grafico_debito.add_trace(go.Bar(x=debito_mes_consolidado['Mês Referência'], y=debito_mes_consolidado['Valor_Orcamento'], 
                                    name='Orçado' ,
                                    marker_color='#708090',
                                    text=debito_mes_consolidado['Valor_Orcamento'],
                                    textposition='auto'))
    grafico_debito.add_trace(go.Bar(x=debito_mes_consolidado['Mês Referência'], y=debito_mes_consolidado['Valor'],
                                     name='Real',
                                     marker_color='#DC143C',
                                     text=debito_mes_consolidado['Valor'],
                                     textposition='auto'))
    
    grafico_debito.update_layout(
        title= 'Orçado vs Real',
        xaxis = dict(title='Mês Referência', showgrid=False),
        yaxis = dict(title='Valores', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)'
    )

    
    debito_classificacao_soma = debito.groupby(['Classificação'])['Valor'].sum().reset_index()
    debito_classificacao_soma_total = debito['Valor'].sum()
    debito_classificacao_soma['Percentual'] = debito_classificacao_soma['Valor'] / debito_classificacao_soma_total  
    debito_classificacao_soma['Percentual'] = round(debito_classificacao_soma['Percentual']*100,2)
    

    grafico_debito_class_med =  go.Figure()

    grafico_debito_class_med.add_trace(go.Bar(x=debito_classificacao_soma['Classificação'],y=debito_classificacao_soma['Percentual'], 
                                              marker_color='#0000FF',
                                              text=debito_classificacao_soma['Percentual'],
                                              textposition='auto'))
    
    grafico_debito_class_med.update_layout(
        title= 'Percentual de gastos por itens total no ano',
        xaxis = dict(title='Itens', showgrid=False),
        yaxis = dict(title='Valores', showgrid=False),
    )

     
    ultima_linha_debito_mes = debito_mes_consolidado.tail(1)
    saldo_atual_debito_mes = float(ultima_linha_debito_mes['Valor_Orcamento'].iloc[0]) - float(ultima_linha_debito_mes['Valor'].iloc[0])               
    st.metric(label='Saldo Mês Atual', value=saldo_atual_debito_mes)
    col1, col2 = st.columns(2)
    
    with col1:
        grafico_debito
    with col2:
        grafico_debito_class_med

with tab4:
    st.title("Análises Crédito")

    lista_mes  = {'1':'1 - janeiro', '2': '2 - fevereiro', '3':'3 - março','4': '4 - abril', '5': '5 - maio','6': '6 - junho', '7': '7 - julho', '8': '8 - agosto','9': '9 - setembro','10': '10 - outubro','11': '11 - novembro', '12': '12 - dezembro'}
    credito['Valor'] = credito['Valor'].str.replace(",",".")
    credito['Valor'] = credito['Valor'].astype(float)
    credito['Mês'] = credito['Mês'].replace(lista_mes)
    orcamento_mensal_credito['Valor'] = orcamento_mensal_credito['Valor'].str.replace(",", ".")
    orcamento_mensal_credito['Valor'] = orcamento_mensal_credito['Valor'].astype(float)
    orcamento_mensal_credito =  orcamento_mensal_credito.rename(columns={'Valor':'Valor_Orcamento'})
    credito = credito.sort_values(by='Mês')
    credito_mes = credito.groupby(['Mês'])['Valor'].sum()
    credito_mes = pd.merge(credito_mes, orcamento_mensal_credito, on ='Mês', how='outer')
    
    credito_mes_nmeses = debito['Mês Referência'].nunique()
    credito_mes_nmeses_bdfiltrada = credito_mes.iloc[0:credito_mes_nmeses, :]
    credito_mes_nmeses_bdfiltrada['Saldo'] = credito_mes_nmeses_bdfiltrada['Valor_Orcamento'] - credito_mes_nmeses_bdfiltrada['Valor']
    credito_mes_nmeses_bdfiltrado_saldo = round(credito_mes_nmeses_bdfiltrada['Saldo'].sum(),2)
    credito_mes_nmeses_bdfiltrado_real = round(credito_mes_nmeses_bdfiltrada['Valor'].sum(),2)
    
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label='Saldo até o mês atual',value=credito_mes_nmeses_bdfiltrado_saldo)
    with col2:
        st.metric(label='Gasto até o mês atual',value=credito_mes_nmeses_bdfiltrado_real)
    

    

    grafico_credito =  go.Figure()
    grafico_credito.add_trace(go.Bar(x= credito_mes['Mês'], y= credito_mes['Valor_Orcamento'],
                                     name='Orçado',
                                     marker_color='#708090',
                                     text=credito_mes['Valor_Orcamento'],
                                     textposition ='auto')) 
    
    grafico_credito.add_trace(go.Bar(x=credito_mes['Mês'], y=credito_mes['Valor'],
                                      name='Real',
                                      marker_color='#DC143C',
                                      text=credito_mes['Valor'],
                                      textposition='auto'))
    
    grafico_credito.update_layout(
        title= 'Orçado vs Real',
        xaxis = dict(title='Mês Referência', showgrid=False),
        yaxis = dict(title='Valores', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    credito_classificacao_agrupado = credito.groupby(['Classificação'])['Valor'].sum().reset_index()
    credito_classificacao_soma = credito['Valor'].sum()
    credito_classificacao_agrupado['Percentual'] = credito_classificacao_agrupado['Valor']/credito_classificacao_soma
    credito_classificacao_agrupado['Percentual'] = round(credito_classificacao_agrupado['Percentual']*100,2)

    grafico_credito_class =  go.Figure()

    grafico_credito_class.add_trace(go.Bar(x=credito_classificacao_agrupado['Classificação'],y=credito_classificacao_agrupado['Percentual'], 
                                              marker_color='#0000FF',
                                              text=credito_classificacao_agrupado['Percentual'],
                                              textposition='auto'))
    
    grafico_credito_class.update_layout(
        title= 'Percentual de gastos por itens total no ano',
        xaxis = dict(title='Itens', showgrid=False),
        yaxis = dict(title='Valores', showgrid=False),
    )
    
    col1, col2 = st.columns(2)

    with col1:
        grafico_credito
    with col2:
        grafico_credito_class

with tab5:
    st.title('Análise VR')

    vr['Valor'] = vr['Valor'].str.replace(',', '.')
    vr['Valor'] = vr['Valor'].astype(float)

    vr_agrupado = vr.groupby(['Mês Referência'])['Valor'].sum()
    vr_agrupado2 = vr.groupby(['Mês Referência', 'Classificação'])['Valor'].sum().reset_index()
    vr_agrupado2



    orcamento_mensal_vr = orcamento_mensal_vr.rename(columns={'Mês': 'Mês Referência'}) 
    orcamento_mensal_vr['Valor'] = orcamento_mensal_vr['Valor'].str.replace(',','.')
    orcamento_mensal_vr['Valor'] = orcamento_mensal_vr['Valor'].astype(float)
    vr_agrupado = pd.merge(vr_agrupado, orcamento_mensal_vr, on='Mês Referência', how='outer')
    

    grafico_vr =  go.Figure()
    grafico_vr.add_trace(go.Bar(x= vr_agrupado['Mês Referência'], y= vr_agrupado['Valor_y'],
                                     name='Orçado',
                                     marker_color='#708090',
                                     text=vr_agrupado['Valor_y'],
                                     textposition ='auto')) 
    
    grafico_vr.add_trace(go.Bar(x= vr_agrupado['Mês Referência'], y= vr_agrupado['Valor_x'],
                                     name='Real',
                                     marker_color='#DC143C',
                                     text=vr_agrupado['Valor_x'],
                                     textposition ='auto'))
    
    grafico_vr.update_layout(
        title= 'Orçado vs Real',
        xaxis = dict(title='Mês Referência', showgrid=False),
        yaxis = dict(title='Valores', showgrid=False),
        plot_bgcolor='rgba(0,0,0,0)'
    )


    grafico_vr_class = px.bar(vr_agrupado2, x='Mês Referência', y='Valor', color='Classificação', barmode='stack')

    col1, col2 =  st.columns(2)
    with col1:
        grafico_vr
    with col2:
        grafico_vr_class