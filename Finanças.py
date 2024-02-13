
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


st.title('Aba de Adição')

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

st.title('Débito')

debito_data = st.text_input('Insirir Data')
debito_descrição =  st.text_input('Insirir Descrição')

debito_classificacao = st.selectbox('Selecione o tipo:', ['Necessidade', 'Lazer - Corinthians', 'Lazer - Outros', 'Lazer - Comida', 'Comida','Casa', 'Passagem','Cabelo','Outros','Classificação'], key='class-debito')
debito_valor = st.text_input('Insirir Valor')
if debito_valor == "":
    debito_valor = 1.0
else:
    debito_valor = debito_valor
debito_valor = float(debito_valor)


novos_debitos = []

with st.form('form'):
    if st.form_submit_button('Adicionar Débito'):
        novo_debito = [debito_data, debito_descrição, debito_classificacao, debito_valor]
        novos_debitos.append(novo_debito)

if novos_debitos:
    novos_debitos_df = pd.DataFrame(novos_debitos, columns=debito.columns)
    worksheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1lEIcy7vjH-X7U1t-toxC6V-ps39f6WQw2mruzTfx1VE/edit#gid=0').get_worksheet(0)
    
    # Obter o número de linhas existentes na planilha
    num_rows = len(worksheet.get_all_values())
    
    # Inserir os dados nas linhas subsequentes
    values_to_insert = novos_debitos_df.values.tolist()
    worksheet.insert_rows(values_to_insert, num_rows + 1) 

debito