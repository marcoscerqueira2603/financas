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

        debito_classificacao = st.selectbox('Selecione o tipo:', ['Necessidade', 'Lazer - Corinthians', 'Lazer - Outros', 'Lazer - Comida', 'Comida','Outros'], key='class-debito')
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
        credito_cartao = st.selectbox('Selecione o cartão:', ['Inter','Nubank','C6'], key='cartao-credito')


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

        orcamento_mes_ref = st.selectbox('Selecione o mês referência:', ['1 - janeiro', '2 - fevereiro', '3 - março', '4 - abril', '5 - maio','6 - junho', '7 - julho','8 - agosto','9 - setembro','10 - outubro','11 - novembro','12 - dezembro'], key='class-orcamento')
        orcamento_salario_base = st.text_input('Insirir Salário', key = "inserir-salário-orçamento")
        orcamento_casa = st.text_input('Insirir Orçamento Casa', key = "inserir-casa-orçamento")
        orcamento_fieltorcedor = st.text_input('Insirir orçamento Fiel Torcedor', key = "inserir-ft-orçamento")
        orcamento_cabelo = st.text_input('Insirir Orçamento Cabelo', key = "inserir-cabelo-orçamento")
        orcamento_celular = st.text_input('Insirir Orçamento Internet Celular', key = "inserir-celular-orçamento")
        orcamento_spotify = st.text_input('Insirir Orçamento Spotify', key = "inserir-spotify-orçamento")
        orcamento_passagem = st.text_input('Insirir Orçamento Passagem', key = "inserir-passagem-orçamento")
        orcamento_segurocel = st.text_input('Insirir Orçamento Seguro Celular', key = "inserir-segurocel-orçamento")
        orcamento_streaming   = st.text_input('Insirir Orçamento Casa', key = "inserir-streaming-orçamento")
        orcamento_tembici = st.text_input('Insirir Orçamento Bike Itau', key = "inserir-bikeitau-orçamento")
        orcamento_crednubank = st.text_input('Insirir Orçamento Crédito Nubank', key = "inserir-crednubank-orçamento")
        orcamento_credinter = st.text_input('Insirir Orçamento Crédito Inter', key = "inserir-credinter-orçamento")
        orcamento_debito = st.text_input('Insirir Orçamento débito', key = "inserir-debito-orçamento")
        orcamento_juntar = st.text_input('Insirir Orçamento juntar', key = "inserir-juntar-orçamento")

        if orcamento_salario_base == "":
            orcamento_salario_base = 1.0
        if orcamento_casa == "":
            orcamento_casa = 1.0
        if orcamento_fieltorcedor == "":
            orcamento_fieltorcedor = 1.0
        if orcamento_cabelo == "":
            orcamento_cabelo = 1.0
        if orcamento_celular == "":
            orcamento_celular = 1.0
        if orcamento_spotify == "":
            orcamento_spotify = 1.0
        if orcamento_passagem == "":
            orcamento_passagem = 1.0
        if orcamento_segurocel == "":
            orcamento_segurocel = 1.0
        if orcamento_streaming == "":
            orcamento_streaming = 1.0
        if orcamento_tembici == "":
            orcamento_tembici = 1.0
        if orcamento_crednubank == "":
            orcamento_crednubank = 1.0
        if orcamento_credinter == "":
            orcamento_credinter = 1.0
        if orcamento_debito == "":
            orcamento_debito = 1.0
        if orcamento_juntar == "":
            orcamento_juntar = 1.0

        soma_gastos = float(orcamento_casa) + float(orcamento_fieltorcedor)  + float(orcamento_cabelo) +  float(orcamento_celular) +  float(orcamento_spotify) + float(orcamento_passagem) + float(orcamento_segurocel)+ float(orcamento_casa)+ float(orcamento_tembici) + float(orcamento_crednubank) + float(orcamento_credinter) + float(orcamento_debito) +float(orcamento_juntar)
        sobra = float(orcamento_salario_base) - soma_gastos

        st.metric(label='Sobra Final', value=sobra)

        orcamento_mensal


        
with tab3:
    st.title("Análises Débitos")
    debito

    debito['Valor'] = debito['Valor'].str.replace(',', '.')
    debito['Valor'] = debito['Valor'].astype(float)
    debito_mes  = debito.groupby(['Mês Referência'])['Valor'].sum()
    debito_mes