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
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader






st.set_page_config(
    page_title="Finanças - Input",
    layout="wide",  initial_sidebar_state='collapsed'
)
    



with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

name, authentication_status, username = authenticator.login('Login', location='main')


if authentication_status:    
    st.session_state["name"] = name
    st.session_state["username"] = username
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
    
    
    
    debito = conn.read(spreadsheet= url_debito, ttl=6000)
    credito = conn.read(spreadsheet= url_credito, ttl=6000)
    receita = conn.read(spreadsheet= url_receitas, ttl=6000)
    fixo = conn.read(spreadsheet= url_extrato_fixos, ttl=6000)
    investimento = conn.read(spreadsheet= url_investimento, ttl=6000)
    emprestimo = conn.read(spreadsheet= url_emprestimos, ttl=6000)
    vr = conn.read(spreadsheet= url_extrato_vr, ttl=6000)
    patrimonio = conn.read(spreadsheet= url_patriomonio, ttl=6000)
    orcamento = conn.read(spreadsheet= url_orcamento, ttl=6000)
    
    
    
    
    
    with st.expander('Débito'):
        st.title('Débito')
    
        if "df_debitos" not in st.session_state:
            st.session_state.df_debitos = pd.DataFrame(columns=["id_mes", "data", "classificacao", "descricao", "debito_compra_credito", "valor", "ano"])
    
    
        with st.form('form débito'):
    
            debito_mes_ref = st.selectbox('Selecione o mês referência:', 
                                        ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_debito')
    
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
                    # Criando um DataFrame com os novos débitos
                    novo_debito = pd.DataFrame([{
                        "id_mes": debito_mes_ref,
                        "data": debito_data,
                        "classificacao": debito_classificacao,
                        "descricao": debito_descricao,
                        "debito_compra_credito": debito_compracredito,
                        "valor": debito_valor,
                        "ano": 2025
                    }])
    
                    # Adiciona ao DataFrame da sessão
                    st.session_state.df_debitos = pd.concat([st.session_state.df_debitos, novo_debito], ignore_index=True)
    
                    st.success("Débito adicionado! Confira na tabela abaixo antes de enviar ao Google Sheets.")
    
    
        st.session_state.df_debitos
            
        if st.button("Enviar ao Google Sheets"):
            df_debito = pd.concat([debito, st.session_state.df_debitos], ignore_index=True)
            
            conn.update(spreadsheet=url_debito, data=df_debito)
            st.success("Débitos enviados com sucesso!")
    
            # Limpa os débitos da sessão
            st.session_state.df_debitos = pd.DataFrame(columns=["id_mes", "data", "classificacao", "descricao", "debito_compra_credito", "valor", "ano"])
    
    
    
    with st.expander('Crédito'):
    
        st.title('Crédito')
    
        if "df_creditos" not in st.session_state:
            st.session_state.df_creditos = pd.DataFrame(columns=['id_mes', 'credito_cartao','descricao','classificacao','valor','ano'])
    
        credito_parcelas =  st.number_input('Inserir Parcelas', value=1)
        meses_disponiveis = ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025']
        credito_mes_parcela1 = st.selectbox('Selecione o mês inicial',  meses_disponiveis) 
        credito_valor = st.text_input('Insirir Valor Crédito', key = 'insirir-valor-credito')
        credito_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-credito')
        credito_classificacao = st.selectbox('Selecione o tipo:', ['Juros/Anuidade','Presente Pitica','Presentes - Família','Lazer','Roupas','Compras Minhas','Outros'], key='class-credito')
        credito_cartao = st.selectbox('Selecione o cartão:', ['Inter','Nubank','C6','Renner'], key='cartao-credito')
    
    
        if credito_valor == "":
            credito_valor = 100.0
        else:
            credito_valor = credito_valor
    
        credito_valor = float(credito_valor)
    
        valor_parcela = round(credito_valor / credito_parcelas, 2)
    
        novos_creditos = []  # Inicializa a lista antes de usá-la
    
        # Exibir formulário no Streamlit
        with st.form('form credito'):
            if st.form_submit_button('Adicionar Gasto Crédito'):
                # Criação das parcelas dentro do formulário
                mes_inicial = datetime.strptime(credito_mes_parcela1, "%m_%Y")
                for i in range(int(credito_parcelas)):
                    id_mes = mes_inicial.strftime("%m_%Y")
                    novo_credito = [id_mes, credito_cartao, credito_descrição, credito_classificacao, valor_parcela,2025]
                    novos_creditos.append(novo_credito)
    
    
                    mes_inicial += relativedelta(months=1)
                novos_creditos_df = pd.DataFrame(novos_creditos, columns=['id_mes', 'credito_cartao','descricao','classificacao','valor','ano' ])
    
                st.session_state.df_creditos = pd.concat([st.session_state.df_creditos, novos_creditos_df], ignore_index=True)
    
                st.success("Crédito adicionado! Confira na tabela abaixo antes de enviar ao Google Sheets.")
            
        st.session_state.df_creditos
            
        if st.button("Enviar ao Google Sheets", key='enviar-sheets-creditos'):
            df_credito = pd.concat([credito, st.session_state.df_creditos], ignore_index=True)
            
            conn.update(spreadsheet=url_credito, data=df_credito)
            st.success("Créditos enviados com sucesso!")
    
            # Limpa os débitos da sessão
            st.session_state.df_creditos = pd.DataFrame(columns=['id_mes', 'credito_cartao','descricao','classificacao','valor','ano'])
    
    
    with st.expander("Receita"): 
        st.title("Receita")
    
        if "df_receitas" not in st.session_state:
            st.session_state.df_receitas = pd.DataFrame(columns=['id_mes', 'data','classificacao','descricao','valor','ano'])
        novos_receitas = []
        with st.form('form receita'):
            receita_data = st.text_input('Insirir Data',key = 'insirir-data-receita ')
            receita_id_mes = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_receita')
            if receita_data  == "":
                receita_data = "08/02/2000"
            else:
                receita_data = receita_data    
    
            
            receita_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-receita')
            receita_classificacao = st.selectbox('Selecione o tipo:', ['Salário','Bônus','13º','Adiantamento Férias','1/3 Férias','Cartola','Apostas','Investimentos','Outros'], key='class-receita')
    
            receita_valor = st.text_input('Insirir Valor', key = 'insirir-valor-receita')
    
            if receita_valor == "":
                receita_valor = 1.0
            else:
                receita_valor = receita_valor
    
            receita_valor = float(receita_valor)
    
        
    
            submit_button = st.form_submit_button("Adicionar Receita")
    
            if submit_button:
                novo_receita = [receita_id_mes, receita_data,  receita_classificacao, receita_descrição, receita_valor,2025]
                novos_receitas.append(novo_receita)
                novos_receitas_df = pd.DataFrame(novos_receitas, columns=['id_mes', 'data','classificacao','descricao','valor','ano'])
    
                st.session_state.df_receitas = pd.concat([st.session_state.df_receitas,novos_receitas_df ], ignore_index=True)
    
                st.success("Receita adicionado! Confira na tabela abaixo antes de enviar ao Google Sheets.")
    
    
    
        st.session_state.df_receitas
            
        if st.button("Enviar ao Google Sheets", key='enviar-sheets-receitas'):
            df_receita = pd.concat([receita, st.session_state.df_receitas], ignore_index=True)
            
            conn.update(spreadsheet=url_receitas, data=df_receita)
    
            st.success("Receitas enviados com sucesso!")
    
            # Limpa os débitos da sessão
            st.session_state.receitas = pd.DataFrame(columns=['id_mes', 'data','classificacao','descricao','valor','ano'])
    
            
        
    with st.expander('Fixos'):
        st.title('Fixos')
        novos_fixos = []
        with st.form('form fixo'):
            fixos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_fixos')
            
            fixos_data = st.text_input('Insirir Data', key = "inserir-data-fixos")
            fixos_descrição =  st.text_input('Insirir Descrição', key = "inserir-descricao-fixos")
    
            fixos_classificacao = st.selectbox('Selecione o tipo:', ['Casa', 'Fiel Torcedor', 'Cabelo', 'Internet - Celular', 'Academia','Passagem', 'Seguro - Celular','Streaming'], key='class-fixos')
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
    
            fixos_algumcredito =  st.selectbox('Gasto em algum crédito?:', ['', 'Nubank','Inter' ], key='class-algumcredito_fixos')
    
    
            submit_button = st.form_submit_button("Adicionar Fixo")
    
            if submit_button:
                novo_fixo= [fixos_mes_ref, fixos_data,fixos_classificacao, fixos_valor , fixos_descrição ,fixos_algumcredito,2025]
                novos_fixos.append(novo_fixo)
                novos_fixos_df = pd.DataFrame(novos_fixos, columns=['id_mes', 'data','classificacao','valor','descricao','fixo_compra_credito','ano'])
    
                fixo_concatenado = pd.concat([fixo, novos_fixos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_extrato_fixos, data=fixo_concatenado)
    
    with st.expander('Patrimônio'):
        novos_patrimonios = []
    
        with st.form('form patrimonio'):
            patrimonio_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                            '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_patrimonio')
    
            patrimonio_valor = st.text_input('Insirir Valor', key = "inserir-valor-patrimonio")
    
            if patrimonio_valor == "":
                patrimonio_valor = 1.0
            else:
                patrimonio_valor = patrimonio_valor
    
            patrimonio_valor = float(patrimonio_valor)
            patrimonio_direcionamento = st.selectbox('Selecione o direcionamento:', ['Patrimônio', 'Reserva Férias'], key='direcionamento-patrimonio')
            patrimonio_classificacao = st.selectbox('Selecione a classificacação:', ['Saldo do mês', '13º','Renda extra','1/3 Férias','Bônus','Emergência','Outros',], key='class-patrimonio')
            patrimonio_descricao =  st.text_input('Insirir Descrição', key = "inserir-descricao-patrimonio")
    
            submit_button = st.form_submit_button("Adicionar Patrimônio")
    
            if submit_button:
                novo_patrimonio= [patrimonio_mes_ref, patrimonio_valor,patrimonio_direcionamento, patrimonio_classificacao , patrimonio_descricao,2025]
    
                novos_patrimonios.append(novo_patrimonio)
                novos_patrimonios_df = pd.DataFrame(novos_patrimonios, columns=['id_mes', 'valor','direcionamento','classificacao','descricao','ano'])
    
                patrimonio_concatenado = pd.concat([patrimonio, novos_patrimonios_df], ignore_index=True)
                
                conn.update(spreadsheet= url_patriomonio, data=patrimonio_concatenado)
    
    with st.expander('Investimentos'):
        st.title('Investimentos')
    
        novos_investimentos = []
        with st.form('form investimentos'):
    
            investimentos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_investimentos')
            
            investimentos_descrição =  st.text_input('Insirir Descrição', key = "inserir-descricao-investimentos")
            investimentos_tipo =  st.text_input('Insirir Tipo Investimentos', key = "inserir-tipo-investimentos")
            investimentos_data = st.text_input('Insirir Data', key = "inserir-data-investimentos")
            investimentos_valor = st.text_input('Insirir Valor', key = "inserir-valor-investimentos")
    
            if investimentos_valor == "":
                investimentos_valor = 1.0
            else:
                investimentos_valor = investimentos_valor
    
            investimentos_valor = float(investimentos_valor)
    
            if investimentos_data  == "":
                investimentos_data = "08/02/2000"
            else:
                investimentos_data = investimentos_data  
    
            
            submit_button = st.form_submit_button("Adicionar Investimento")
    
            if submit_button:
                novos_investimento= [investimentos_mes_ref, investimentos_descrição,investimentos_tipo, investimentos_data, investimentos_valor, 2025]
                novos_investimentos.append(novos_investimento)
                novos_investimentos_df = pd.DataFrame(novos_investimentos, columns=['id_mes', 'descricao','investimento_tipo','data','valor','ano'])
    
                investimentos_concatenados = pd.concat([investimento, novos_investimentos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_investimento, data=investimentos_concatenados)
    
    
    with st.expander('Empréstimos'):
        st.title('Empréstimos')
        novos_emprestimos = []
        with st.form('form emprestimos'):
            emprestimos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_emprestimos')
            
            emprestimos_descrição =  st.text_input('Insirir Descrição', key = "inserir-descricao-emprestimos")
            emprestimos_destinatario =  st.text_input('Insirir Destinatário', key = "inserir-destinatario-emprestimos")
    
            emprestimos_data = st.text_input('Insirir Data', key = "inserir-data-emprestimos")
            emprestimos_valor = st.text_input('Insirir Valor', key = "inserir-valor-emprestimos")
    
            if emprestimos_valor == "":
                emprestimos_valor = 1.0
            else:
                emprestimos_valor = emprestimos_valor
    
            emprestimos_valor = float(emprestimos_valor)
    
            if emprestimos_data  == "":
                emprestimos_data = "08/02/2000"
            else:
                emprestimos_data = emprestimos_data
    
    
            submit_button = st.form_submit_button("Adicionar empréstimo")
    
            if submit_button:
                novo_emprestimo= [emprestimos_mes_ref, emprestimos_descrição,emprestimos_destinatario, emprestimos_data, emprestimos_valor,2025]
                novos_emprestimos.append(novo_emprestimo)
                novos_emprestimos_df = pd.DataFrame(novos_emprestimos, columns=['id_mes', 'descricao','emprestimo_destinatario','data','valor','ano'])
    
                emprestimos_concatenados = pd.concat([emprestimo, novos_emprestimos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_emprestimos, data=emprestimos_concatenados)
                
    
        
    
    with st.expander('VR'):
            st.title('VR')
            novos_vrs = []
            with st.form('form vr'):
                #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição
    
                #a partir do calculo de data conseguimos ter o mes e jogamos lá
                vr_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_vr')
    
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
    
    
    
                submit_button = st.form_submit_button("Adicionar VR")
    
                if submit_button:
                    novo_vr = [ vr_data, vr_mes_ref, vr_descrição,vr_local,  vr_classificacao, vr_valor,2025]
                    novos_vrs.append(novo_vr)
                    novos_vrs_df = pd.DataFrame(novos_vrs, columns=['data', 'id_mes', 'descricao','local','classificacao','valor','ano'])
    
                    vr_concatenado = pd.concat([vr, novos_vrs_df], ignore_index=True)
                    
                    conn.update(spreadsheet= url_extrato_vr, data=vr_concatenado)


elif st.session_state["authentication_status"] is False:
    st.error("Usuário ou senha incorretos")
elif st.session_state["authentication_status"] is None:
    st.warning("Insira um usuário ou senha")
