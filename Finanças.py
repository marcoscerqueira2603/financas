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



debito = conn.read(spreadsheet= url_debito)
credito = conn.read(spreadsheet= url_credito)
receita = conn.read(spreadsheet= url_receitas)
fixo = conn.read(spreadsheet= url_extrato_fixos)
investimento = conn.read(spreadsheet= url_investimento)
emprestimo = conn.read(spreadsheet= url_emprestimos)
vr = conn.read(spreadsheet= url_extrato_vr)
patrimonio = conn.read(spreadsheet= url_patriomonio)
orcamento = conn.read(spreadsheet= url_orcamento)


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
 

                # Adiciona o novo débito à lista de débitos
                novo_debito = [debito_mes_ref, debito_data, debito_classificacao, debito_descricao, debito_compracredito, debito_valor]
                novos_debitos.append(novo_debito)

                novos_debitos_df = pd.DataFrame(novos_debitos, columns=["id_mes", "data", "classificacao", "descricao", "debito_compra_credito", "valor"])
                debito_concatenado = pd.concat([debito, novos_debitos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_debito, data=debito_concatenado)

    with st.expander('Crédito'):

        st.title('Crédito')

        credito_parcelas =  st.number_input('Inserir Parcelas', value=1)
        meses_disponiveis = ['01_2024', '02_2024', '03_2024', '04_2024', '05_2024', '06_2024', '07_2024', '08_2024','09_2024','10_2024','11_2024','12_2024']
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
                    novo_credito = [id_mes, credito_cartao, credito_descrição, credito_classificacao, valor_parcela]
                    novos_creditos.append(novo_credito)


                    # Avançar para o próximo mês
                    mes_inicial += relativedelta(months=1)
                novos_creditos_df = pd.DataFrame(novos_creditos, columns=['id_mes', 'credito_cartao','descricao','classificacao','valor' ])

                credito_concatenado = pd.concat([credito,novos_creditos_df], ignore_index=True)
                conn.update(spreadsheet= url_credito, data=credito_concatenado)
            
    with st.expander("Receita"): 
        st.title("Receita")
        novos_receitas = []
        with st.form('form receita'):
            receita_data = st.text_input('Insirir Data',key = 'insirir-data-receita ')
            receita_id_mes = st.selectbox('Selecione o mês referência:', ['01_2024','02_2024','03_2024','04_2024','05_2024','06_2024','07_2024','08_2024','09_2024','10_2024','11_2024','12_2024'], key='class-mesref_receita')
            if receita_data  == "":
                receita_data = "08/02/2000"
            else:
                receita_data = receita_data    

            
            receita_descrição =  st.text_input('Insirir Descrição', key = 'insirir-descricao-receita')
            receita_classificacao = st.selectbox('Selecione o tipo:', ['Salário','Bônus','13º','Cartola','Apostas','Investimentos','Outros'], key='class-receita')

            receita_valor = st.text_input('Insirir Valor', key = 'insirir-valor-receita')

            if receita_valor == "":
                receita_valor = 1.0
            else:
                receita_valor = receita_valor

            receita_valor = float(receita_valor)

        

            submit_button = st.form_submit_button("Adicionar Receita")

            if submit_button:
                novo_receita = [receita_id_mes, receita_data,  receita_classificacao, receita_descrição, receita_valor]
                novos_receitas.append(novo_receita)
                novos_receitas_df = pd.DataFrame(novos_receitas, columns=['id_mes', 'data','classificacao','descricao','valor'])



                receita_concatenado = pd.concat([receita, novos_receitas_df], ignore_index=True)
                
                conn.update(spreadsheet= url_receitas, data=receita_concatenado)
        
    with st.expander('Fixos'):
        st.title('Fixos')
        novos_fixos = []
        with st.form('form fixo'):
            fixos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2024','02_2024','03_2024','04_2024','05_2024',
                                                                            '06_2024','07_2024','08_2024','09_2024','10_2024',
                                                                            '11_2024','12_2024'], key='class-mesref_fixos')
            
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
                novo_fixo= [fixos_mes_ref, fixos_data,fixos_classificacao, fixos_valor , fixos_descrição ,fixos_algumcredito]
                novos_fixos.append(novo_fixo)
                novos_fixos_df = pd.DataFrame(novos_fixos, columns=['id_mes', 'data','classificacao','valor','descricao','fixo_compra_credito'])

                fixo_concatenado = pd.concat([fixo, novos_fixos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_extrato_fixos, data=fixo_concatenado)

    with st.expander('Investimentos'):
        st.title('Investimentos')

        novos_investimentos = []
        with st.form('form investimentos'):

            investimentos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2024','02_2024','03_2024','04_2024','05_2024',
                                                                            '06_2024','07_2024','08_2024','09_2024','10_2024',
                                                                            '11_2024','12_2024'], key='class-mesref_investimentos')
            
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

            
            submit_button = st.form_submit_button("Adicionar Fixo")

            if submit_button:
                novos_investimento= [investimentos_mes_ref, investimentos_descrição,investimentos_tipo, investimentos_data, investimentos_valor]
                novos_investimentos.append(novos_investimento)
                novos_investimentos_df = pd.DataFrame(novos_investimentos, columns=['id_mes', 'descricao','investimento_tipo','data','valor'])

                investimentos_concatenados = pd.concat([investimento, novos_investimentos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_investimento, data=investimentos_concatenados)


    with st.expander('Empréstimos'):
        st.title('Empréstimos')
        novos_emprestimos = []
        with st.form('form emprestimos'):
            emprestimos_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2024','02_2024','03_2024','04_2024','05_2024',
                                                                            '06_2024','07_2024','08_2024','09_2024','10_2024',
                                                                            '11_2024','12_2024'], key='class-mesref_emprestimos')
            
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
                novo_emprestimo= [emprestimos_mes_ref, emprestimos_descrição,emprestimos_destinatario, emprestimos_data, emprestimos_valor]
                novos_emprestimos.append(novo_emprestimo)
                novos_emprestimos_df = pd.DataFrame(novos_emprestimos, columns=['id_mes', 'descricao','emprestimo_destinatario','data','valor'])

                emprestimos_concatenados = pd.concat([emprestimo, novos_emprestimos_df], ignore_index=True)
                
                conn.update(spreadsheet= url_emprestimos, data=emprestimos_concatenados)
                

        

    with st.expander('VR'):
            st.title('VR')
            novos_vrs = []
            with st.form('form vr'):
                #adicionando dados relativos a aba de débito: incluem a data, a classificação, o valor, a descrição

                #a partir do calculo de data conseguimos ter o mes e jogamos lá
                vr_mes_ref = st.selectbox('Selecione o mês referência:', ['01_2024','02_2024','03_2024','04_2024','05_2024',
                                                                                '06_2024','07_2024','08_2024','09_2024','10_2024',
                                                                                '11_2024','12_2024'], key='class-mesref_vr')
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
                    novo_vr = [ vr_data, vr_mes_ref, vr_descrição,vr_local,  vr_classificacao, vr_valor]
                    novos_vrs.append(novo_vr)
                    novos_vrs_df = pd.DataFrame(novos_vrs, columns=['data', 'id_mes', 'descricao','local','classificacao','valor'])

                    vr_concatenado = pd.concat([vr, novos_vrs_df], ignore_index=True)
                    
                    conn.update(spreadsheet= url_extrato_vr, data=vr_concatenado)



  
with tab2:

    #agrupando planilhas de gastos mensais
    fixo_agrupado = fixo.groupby(['id_mes', 'classificacao'])['valor'].sum().reset_index()
    debito_agrupado = debito.groupby(['id_mes'])['valor'].sum().reset_index()
    debito_agrupado['classificacao'] = 'Débito'
    credito_agrupado = credito.groupby(['id_mes'])['valor'].sum().reset_index()
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
        debito_agrupado_class =  debito.groupby(['id_mes','classificacao'])['valor'].sum().reset_index()
        
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
            filtro_id_mes = st.multiselect('Selecione o mês',debito['id_mes'].unique(),list(debito['id_mes'].unique()))
            debito_filtrado = debito[debito['id_mes'].isin(filtro_id_mes)]
            filtro_class = st.multiselect('Selecione a classificação',debito_filtrado['classificacao'].unique(),list(debito_filtrado['classificacao'].unique()))
            debito_filtrado = debito_filtrado[debito_filtrado['classificacao'].isin(filtro_class)]
        debito_filtrado

    with st.expander('Status Crédito'):
        #criacao dos mestricos
        
        credito_orcamento =  orcamento_unificado[orcamento_unificado['classificacao'] == 'Crédito']
        
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
        
        credito_agrupado_class =  credito.groupby(['id_mes','classificacao'])['valor'].sum().reset_index()
        
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
            filtro_id_mes_credito = st.multiselect('Selecione o mês',credito['id_mes'].unique(),list(credito['id_mes'].unique()))
            credito_filtrado = credito[credito['id_mes'].isin(filtro_id_mes_credito)]
            filtro_class_credito = st.multiselect('Selecione a classificação',credito_filtrado['classificacao'].unique(),list(credito_filtrado['classificacao'].unique()))
            credito_filtrado = credito_filtrado[credito_filtrado['classificacao'].isin(filtro_class_credito)]
        credito_filtrado