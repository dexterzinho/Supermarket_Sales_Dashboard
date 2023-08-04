#Importando Bibliotecas
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

load_figure_template('yeti')
app = dash.Dash(external_stylesheets=[dbc.themes.YETI])
server = app.server

df = pd.read_csv('supermarket_sales.csv')
df['Date'] = pd.to_datetime(df['Date'])
#df['City'].value_counts().index
df['Avaliação'] = df['Rating']
df['Receita'] = df['gross income']
df.drop('Rating', axis=1, inplace=True)
df.drop('gross income', axis=1, inplace=True)


#============== Layout =======================
app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                html.H1(children='DASHBOARD PROJETO SUPERMARKET SALES', style={'font-family':'Poppins', 'font-weight':'950'}),
                html.Hr(),
                html.H3(children='Cidades:',style={'margin-top':'30px'}),
                dcc.Checklist(df['City'].value_counts().index, inline=True, value=df['City'].value_counts().index, id='check_city', inputStyle={'margin-right': '5px', 'margin-left': '15px'}),
                html.H4(children='Escolha o parâmetro:', style={'margin-top':'30px'}),
                dcc.RadioItems(options=['Receita', 'Avaliação'], value='Receita', inline=True, id='parametro', inputStyle={'margin-right': '5px', 'margin-left': '25px'}),
                html.Img(src=app.get_asset_url('SUPERMARKET LOGO.jpg'))
            ], style={'height':'95vh', 'margin': '10px', 'padding':'10px'})
        ], sm=3),

        dbc.Col([
            dbc.Row([
                dbc.Col([dcc.Graph(id='pay_fig')], sm=4),
                dbc.Col([dcc.Graph(id='city_fig')], sm=4),
                dbc.Col([dcc.Graph(id='gender_fig')], sm=4)
            ]),
            dbc.Row([dcc.Graph(id='income_per_date_fig')]),
            dbc.Row([dcc.Graph(id='income_per_product_fig')])    
        ], sm=9)
    ])
])

#================= Callbacks ===================
@app.callback([
    Output('pay_fig', 'figure'),
    Output('city_fig', 'figure'),
    Output('gender_fig', 'figure'),
    Output('income_per_date_fig', 'figure'),
    Output('income_per_product_fig', 'figure')],
    [Input('check_city', 'value'),
    Input('parametro', 'value')])
def gerar_graficos(cities, parametro,):
    #TESTE
    #cities = ['Yangon', 'Mandalay']
    #parametro = 'Receita'

    operation = np.sum if parametro == 'Receita' else np.mean
    df_filtered = df[df['City'].isin(cities)]
    df_city = df_filtered.groupby('City')[parametro].apply(operation).to_frame().reset_index()
    df_gender = df_filtered.groupby(['Gender', 'City'])[parametro].apply(operation).to_frame().reset_index()
    df_payment = df_filtered.groupby('Payment')[parametro].apply(operation).to_frame().reset_index()
    df_product_income = df_filtered.groupby(['Product line', 'City'])[parametro].apply(operation).to_frame().reset_index()
    df_income_per_date = df_filtered.groupby('Date')[parametro].apply(operation).to_frame().reset_index()

    
    fig_city = px.bar(df_city, df_city['City'], y=parametro, color=df_city['City'])  
    fig_payment = px.bar(df_payment, y=df_payment['Payment'], x=parametro, color=df_payment['Payment'], orientation='h')
    fig_gender = px.bar(df_gender, y=parametro, x=df_gender['Gender'], color=df_gender['City'], barmode='group')  
    fig_product_income = px.bar(df_product_income, x=parametro, y=df_product_income['Product line'], color=df_product_income['City'],  orientation='h', barmode='group')  
    fig_income_per_date = px.bar(df_income_per_date, x=df_income_per_date['Date'], y=parametro)  


    for fig in [fig_city, fig_payment, fig_gender, fig_income_per_date]:
        fig.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=200, template='yeti')

    fig_product_income.update_layout(margin=dict(l=0, r=0, t=20, b=20), height=500, template='yeti')


    return fig_payment, fig_city, fig_gender, fig_income_per_date, fig_product_income




#================ Run Server ====================
if __name__ == '__main__':
    app.run_server(port=8050, debug=False)