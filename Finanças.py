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
    page_title="Finanças",
    layout="wide"
)

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



debito = conn.read(spreadsheet= url_debito, ttl=300)
credito = conn.read(spreadsheet= url_credito, ttl=300)
receita = conn.read(spreadsheet= url_receitas, ttl=300)
fixo = conn.read(spreadsheet= url_extrato_fixos, ttl=300)
investimento = conn.read(spreadsheet= url_investimento, ttl=300)
emprestimo = conn.read(spreadsheet= url_emprestimos, ttl=300)
vr = conn.read(spreadsheet= url_extrato_vr, ttl=300)
patrimonio = conn.read(spreadsheet= url_patriomonio, ttl=300)
orcamento = conn.read(spreadsheet= url_orcamento, ttl=300)




tab1, tab2 = st.tabs(['Adicionar dados','Visualização'])

with tab1:

    with st.expander('Débito'):
        st.title('Débito')

        #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição
        novos_debitos = []


        with st.form('form débito'):
            # Campos para inserir as informações do débito
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
 

                # Adiciona o novo débito à lista de débitos
                novo_debito = [debito_mes_ref, debito_data, debito_classificacao, debito_descricao, debito_compracredito, debito_valor,2025]
                novos_debitos.append(novo_debito)

                novos_debitos_df = pd.DataFrame(novos_debitos, columns=["id_mes", "data", "classificacao", "descricao", "debito_compra_credito", "valor",'ano'])
                debito_concatenado = pd.concat([debito, novos_debitos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_debito, data=debito_concatenado)

    with st.expander('Crédito'):

        st.title('Crédito')

        credito_parcelas =  st.number_input('Inserir Parcelas', value=1)
        meses_disponiveis = ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025']
        credito_mes_parcela1 = st.selectbox('Selecione o mês inicial',  meses_disponiveis) 
        credito_valor = st.text_input('Insirir Valor Crédito', key = 'insirir-valor-credito')
        credito_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-credito')
        credito_classificacao = st.selectbox('Selecione o tipo:', ['Faturas 2023','Presente Pitica','Presentes - Família','Lazer','Roupas','Compras Minhas','Outros'], key='class-credito')
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


                    # Avançar para o próximo mês
                    mes_inicial += relativedelta(months=1)
                novos_creditos_df = pd.DataFrame(novos_creditos, columns=['id_mes', 'credito_cartao','descricao','classificacao','valor','ano' ])

                credito_concatenado = pd.concat([credito,novos_creditos_df], ignore_index=True)
                conn.update(spreadsheet= url_credito, data=credito_concatenado)
            
    with st.expander("Receita"): 
        st.title("Receita")
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



                receita_concatenado = pd.concat([receita, novos_receitas_df], ignore_index=True)
                
                conn.update(spreadsheet= url_receitas, data=receita_concatenado)
        
    with st.expander('Fixos'):
        st.title('Fixos')
        novos_fixos = []
        with st.form('form fixo'):
            fixos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2025','02_2025','03_2025','04_2025','05_2025','06_2025','07_2025',
                                        '08_2025','09_2025','10_2025','11_2025','12_2025'], key='class-mesref_fixos')
            
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


            submit_button = st.form_submit_button("Adicionar Fixo")

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



  
with tab2:

    



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
        investimento
