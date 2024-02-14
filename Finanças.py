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

tab1,tab2 = st.tabs(['Incluir Dados', 'Construir'])

with tab1:   
    with st.expander('Débito'):
        st.title('Débito')

        #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição

        #a partir do calculo de data conseguimos ter o mes e jogamos lá

        debito_data = st.text_input('Insirir Data', key = "inserir-data-debito")
        debito_descrição =  st.text_input('Insirir Descrição', key = "inserir-descricao-debito")

        debito_classificacao = st.selectbox('Selecione o tipo:', ['Necessidade', 'Lazer - Corinthians', 'Lazer - Outros', 'Lazer - Comida', 'Comida','Casa', 'Passagem','Cabelo','Outros','Classificação'], key='class-debito')
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

        debito_date_obj = datetime.strptime(debito_data, "%d/%m/%Y")
        debito_mes   = debito_date_obj.month

        novos_debitos = []

        with st.form('form débito'):
            if st.form_submit_button('Adicionar Débito'):
                novo_debito = [debito_data, debito_mes, debito_descrição, debito_classificacao, debito_valor]
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

            vr_date_obj = datetime.strptime(vr_data, "%d/%m/%Y")
            vr_mes   = vr_date_obj.month

            novos_vrs = []

            with st.form('form vr'):
                if st.form_submit_button('Adicionar Gastor VR'):
                    novo_vr = [vr_data, vr_mes, vr_descrição,vr_local,  vr_classificacao, vr_valor]
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