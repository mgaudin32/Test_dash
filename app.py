# coding: utf-8

##########
# Import libraries
##########
import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go

import warnings
warnings.filterwarnings("ignore")

##########
# Récupération des données
##########
df = pd.read_csv('./df.zip', sep=',', index_col = 'Date')
df.index = pd.to_datetime(df.index)

##########
# Datas pour les 2 roues et 4 roues
##########
deux_roues = [1, 2, 30, 31, 32, 33, 34]
deux_roues_df = df.loc[df['catv'].isin(deux_roues)]
catveh = dict({1 : 'Bicyclette', 2:'Cyclomoteur <50cm3', 30: 'Scooter < 50 cm3', 31 : 'Motocyclette > 50 cm3 et <= 125 cm3', 32 : 'Scooter > 50 cm3 et <= 125 cm3', 33: 'Motocyclette > 125 cm3', 34 : 'Scooter > 125 cm3'})
deux_roues_df['catv'] = deux_roues_df['catv'].map(catveh)

quatre_roues = [35, 36, 7, 10, 14, 15, 16, 17]
quatre_roues_df = df.loc[df['catv'].isin(quatre_roues)]
cat_quatre_veh = dict({35 : 'Quad leger <= 50cm3', 36:'Quad lourd > 50cm3', 7: 'VL seul', 10 : 'VU seul <= 3.5T', 14 : 'PL seul > 7.5T', 15: 'PL >3.5T + remorque', 
               16 : 'Tracteur routier seul', 17:'Tracteur routier + semi-remorque'})
quatre_roues_df['catv'] = quatre_roues_df['catv'].map(cat_quatre_veh)

gravveh = dict({1 : 'Indemne', 2:'Tue', 3: 'Blesse hospitalise', 4 : 'Blesse leger'})
deux_roues_df['grav'] = deux_roues_df['grav'].map(gravveh)
quatre_roues_df['grav'] = quatre_roues_df['grav'].map(gravveh)

trajveh = dict({1 : 'Domicile-Travail', 2:'Domicile-Ecole', 3: 'Courses/Achats', 4 : 'Professionnelle', 5 : 'Promenade/Loisirs', 9 : 'Autre'})
deux_roues_df['trajet'] = deux_roues_df['trajet'].map(trajveh)
quatre_roues_df['trajet'] = quatre_roues_df['trajet'].map(trajveh)

obsveh = dict({1 : 'Véhicule en stationnement', 2 : 'Arbre', 3 : 'Glissière métallique', 4 : 'Glissière béton', 5 : 'Autre glissière', 6 : 'Bâtiment, mur, pile de pont',
7 : 'Support de signalisation', 8 : 'Poteau', 9 : 'Mobilier urbain', 10 : 'Parapet', 11 : 'Ilot, refuge, borne haute', 12 : 'Bordure de trottoir', 
13 : 'Fossé, talus, paroi rocheuse', 14 : 'Autre obstacle fixe sur chaussée', 15 : 'Autre obstacle fixe sur trottoir ou accotement', 16 : 'Sortie de chaussée sans obstacle' })
deux_roues_df['obs'] = deux_roues_df['obs'].map(obsveh)
quatre_roues_df['obs'] = quatre_roues_df['obs'].map(obsveh)

obsmveh = dict({1 : 'Pieton', 2 : 'Vehicule', 4 : 'Train', 5 : 'Animal domestique', 6 : 'Animal sauvage', 9 : 'Autre'} )
deux_roues_df['obsm'] = deux_roues_df['obsm'].map(obsmveh)
quatre_roues_df['obsm'] = quatre_roues_df['obsm'].map(obsmveh)

##########
# Dataframe evolution du nombre de blesses par jour/semaine/mois/annees en fonction de la catégorie du 2 roues
##########
dr_per_day = deux_roues_df.groupby('catv').resample('d').sum()['Unit'].to_frame().reset_index('catv')
dr_per_week = deux_roues_df.groupby('catv').resample('w').sum()['Unit'].to_frame().reset_index('catv')
dr_per_month = deux_roues_df.groupby('catv').resample('m').sum()['Unit'].to_frame().reset_index('catv')
dr_per_year = deux_roues_df.groupby('catv').resample('y').sum()['Unit'].to_frame().reset_index('catv')

dr_per_month = dr_per_month.sort_index()
dr_per_month['Ratio'] = round(((dr_per_month['Unit'] / dr_per_month.groupby('Date').sum()['Unit'])*100),2)
dr_per_month['strDate'] = dr_per_month.index.astype(str)

dr_per_year = dr_per_year.sort_index()
dr_per_year['Ratio'] = round(((dr_per_year['Unit'] / dr_per_year.groupby('Date').sum()['Unit'])*100),2)
dr_per_year['strDate'] = dr_per_year.index.astype(str)

dr_per_day = dr_per_day.sort_index()
dr_per_day['Ratio'] = round(((dr_per_day['Unit'] / dr_per_day.groupby('Date').sum()['Unit'])*100),2)
dr_per_day['strDate'] = dr_per_day.index.astype(str)

##########
# Dataframe evolution du nombre de blesses par jour/semaine/mois/annees en fonction de la catégorie du 4 roues
##########
qr_per_day = quatre_roues_df.groupby('catv').resample('d').sum()['Unit'].to_frame().reset_index('catv')
qr_per_week = quatre_roues_df.groupby('catv').resample('w').sum()['Unit'].to_frame().reset_index('catv')
qr_per_month = quatre_roues_df.groupby('catv').resample('m').sum()['Unit'].to_frame().reset_index('catv')
qr_per_year = quatre_roues_df.groupby('catv').resample('y').sum()['Unit'].to_frame().reset_index('catv')

##########
# Dash App
##########
# Set up the app
# external_stylesheets = ['https://raw.githubusercontent.com/plotly/dash-sample-apps/master/apps/dash-oil-and-gas/assets/s1.css']

app = dash.Dash(
    __name__)

server = app.server


def create_dict_list_of_vehicules():
    dictlist = []
    unique_list = deux_roues_df['catv'].unique()
    for vehicule in unique_list:
        dictlist.append({'value': vehicule, 'label':vehicule})
    return dictlist

def create_dict_list_of_vehicules_quatre():
    dictlist = []
    unique_list = quatre_roues_df['catv'].unique()
    for vehicule in unique_list:
        dictlist.append({'value': vehicule, 'label':vehicule})
    return dictlist

def dict_vehicule_list(dictlist):
    vehicule_list = []
    for d in dictlist:
        vehicule_list.append(dict.get('value'))
    return vehicule_list

def create_dict_list_of_years():
    dict_years = []
    unique_years = dr_per_year.index.year.unique()
    for year in unique_years:
        dict_years.append({'value': year, 'label':year})
    return dict_years

dict_vehicules = create_dict_list_of_vehicules()
dict_years = create_dict_list_of_years()
dict_vehicules_quatre=create_dict_list_of_vehicules_quatre()


# 2 roues evolution line plot
app.layout = html.Div([
    html.H1("France : accidents de la route", style={'textAlign': 'center', 'margin-bottom':'0px', 'margin-top': '50px'}),
    html.H2("Accidents corporels", style={'textAlign': 'center', 'margin-bottom':'50px', 'margin-top': '0px'}),
    html.Div([
        html.H3('Evolution des 2 roues'),
        html.P('Choisir un (des) véhicule(s) :'),
        dcc.Dropdown(
            id='vehicule-dropdown',
            options=dict_vehicules,
            multi=True,
            value = ["Bicyclette"]
        ),
        dcc.Graph(
            id='vehicule-like-bar', style ={'box-shadow': '2px 2px 2px lightgrey'}
        )
    ], style={'margin-left':'50px', 'width': '45%', 'display': 'inline-block'}),

# 4 roues evolution line plot
    html.Div([
    html.H3('Evolution des 4 roues'),
    html.P('Choisir un (des) véhicule(s) :'),
    dcc.Dropdown(
            id='quatre-dropdown',
            options=dict_vehicules_quatre,
            multi=True,
            value = ["VL seul"]
        ),
        dcc.Graph(
            id='quatre-like-bar', style ={'box-shadow': '2px 2px 2px lightgrey'}
        )
    ], style={'margin-left':'50px','width': '45%', 'display': 'inline-block', 'padding': '0px 50px 1px'}),
 
# 2 roues evolution Range Slider
    html.Div([
        html.P("Filter by date (or range of date):"),
        dcc.RangeSlider(
            id='crossfilter-year--slider',
            min=deux_roues_df.index.year.min(),
            max=deux_roues_df.index.year.max(),
            value=[deux_roues_df.index.year.min(),deux_roues_df.index.year.max()],
            marks={str(year) : {'label' : str(year), 'style':{'width': 50}} for year in deux_roues_df.index.year.unique()},
            step=None
        )],style={'margin-left':'50px','width': '35%', 'display': 'inline-block', 'padding': '20px 0px 10px 80px'}),

    
# 4 roues evolution Range Slider
    html.Div([
        html.P("Filter by date (or range of date):"),
        dcc.RangeSlider(
            id='quatre-year--slider',
            min=quatre_roues_df.index.year.min(),
            max=quatre_roues_df.index.year.max(),
            value=[quatre_roues_df.index.year.min(),quatre_roues_df.index.year.max()],
            marks={str(year): str(year) for year in quatre_roues_df.index.year.unique()},
            step=None
        )],style={'margin-left':'50px','width': '35%', 'display': 'inline-block', 'padding': '20px 0px 10px 280px'}),
    
# 2 roues evolution Bar
    html.Div([
        dcc.Graph(
            id='count-blesse', style ={'box-shadow': '2px 2px 2px lightgrey'}
                )], style={'margin-left':'50px', 'margin-top':'20px','width': '45%', 'display': 'inline-block'}),

# 4 roues evolution Bar
   html.Div([
        dcc.Graph(
            id='quatre-count-blesse', style ={'box-shadow': '2px 2px 2px lightgrey'}
                )], style={'margin-left':'50px','margin-top':'20px','width': '45%', 'display': 'inline-block', 'padding': '0px 50px 1px'}),
    
# 2 roues evolution PieChart 
    html.Div([
        html.H3('Répartition par année'),
        dcc.Dropdown(
            id='annee-dropdown',
            options=dict_years,
            placeholder="Select a year",
            multi=False,
            value = '2005',
            style={'margin-left':'50px','width': '120px'}
        ),
        dcc.Graph(id='pie-chart-graph', style ={'box-shadow': '2px 2px 2px lightgrey'})
    ], style={'margin-left':'50px','width': '45%',  'display': 'inline-block'}),

# 4 roues evolution PieChart
    html.Div([
        html.H3('Répartition par année'),
        dcc.Dropdown(
            id='quatre-annee-dropdown',
            options=dict_years,
            placeholder="Select a year",
            multi=False,
            value = '2005',
            style={'margin-left':'50px','width': '120px'}
        ),
        dcc.Graph(id='quatre-pie-chart-graph', style ={'box-shadow': '2px 2px 2px lightgrey'})
    ], style={'margin-left':'50px','width': '45%',  'display': 'inline-block', 'padding': '0px 50px 1px'}),
   
])

@app.callback(Output('vehicule-like-bar', 'figure'), [Input('vehicule-dropdown', 'value'), Input('crossfilter-year--slider', 'value')])
def update_graph(selected_dropdown_value, date_value):
    dr_per_month_date = dr_per_month[str(date_value[0]):str(date_value[1])]
    dr_per_month_filter = dr_per_month_date[(dr_per_month_date['catv'].isin(selected_dropdown_value))]

    figure = px.line(dr_per_month_filter, x=dr_per_month_filter.index, y='Unit', color ='catv')
    # Use date string to set xaxis range
#     figure.update_layout(title_text="Manually Set Date Range", margin={'b': 0})
    figure.update_layout(font=dict(size=18))
    figure.update_layout(legend=dict(font=dict(
            size=15)))
    return figure

@app.callback(Output('quatre-like-bar', 'figure'), [Input('quatre-dropdown', 'value'), Input('quatre-year--slider', 'value')])
def update_graph(selected_dropdown_value, date_value):
    qr_per_month_date = qr_per_month[str(date_value[0]):str(date_value[1])]
    qr_per_month_filter = qr_per_month_date[(qr_per_month_date['catv'].isin(selected_dropdown_value))]

    figure = px.line(qr_per_month_filter, x=qr_per_month_filter.index, y='Unit', color ='catv')
    # Use date string to set xaxis range
#     figure.update_layout(title_text="Manually Set Date Range", margin={'b': 0})
    figure.update_layout(font=dict(size=18))
    figure.update_layout(legend=dict(font=dict(
            size=15)))
    return figure

@app.callback(Output('pie-chart-graph', 'figure'), [Input('annee-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    #defining data
    selected_dropdown_value = str(selected_dropdown_value)
    data=[go.Pie(labels=dr_per_year[selected_dropdown_value]['catv'].values, values=dr_per_year[selected_dropdown_value]['Unit'].values, hole = 0.4)]
    #defining figure and plotting
    figure = go.Figure(data)
    figure.update_layout(font=dict(size=18))
    return figure

@app.callback(Output('quatre-pie-chart-graph', 'figure'), [Input('quatre-annee-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    #defining data
    selected_dropdown_value = str(selected_dropdown_value)
    data=[go.Pie(labels=qr_per_year[selected_dropdown_value]['catv'].values, values=qr_per_year[selected_dropdown_value]['Unit'].values, hole = 0.4)]
    #defining figure and plotting
    figure = go.Figure(data)
    figure.update_layout(font=dict(size=18))
    return figure

@app.callback(Output('count-blesse', 'figure'), [Input('crossfilter-year--slider', 'value'), Input('vehicule-dropdown', 'value')])
def update_graph(date_value, vehicule_dropdown):
    deux_roues_df_date = deux_roues_df[str(date_value[0]):str(date_value[1])]
    deux_roues_df_filter = deux_roues_df_date[(deux_roues_df_date['catv'].isin(vehicule_dropdown))]
    grav_df = deux_roues_df_filter.groupby(['grav', 'catv']).sum()
    grav_df['Ratio'] = round((grav_df['Unit'] / grav_df['Unit'].sum())*100, 2)
    figure = px.bar(grav_df, x=grav_df.index.get_level_values(0), y='Ratio', color = grav_df.index.get_level_values(1), text='Ratio')
    figure.update_layout(xaxis_title="Etat", 
                         yaxis_title="Proportion (%)",
                         font=dict(size=18))
    figure.update_yaxes(range=[0, 100])
   
    return figure

@app.callback(Output('quatre-count-blesse', 'figure'), [Input('quatre-year--slider', 'value'), Input('quatre-dropdown', 'value')])
def update_graph(date_value, vehicule_dropdown):
    quatre_roues_df_date = quatre_roues_df[str(date_value[0]):str(date_value[1])]
    quatre_roues_df_filter = quatre_roues_df_date[(quatre_roues_df_date['catv'].isin(vehicule_dropdown))]
    grav_df = quatre_roues_df_filter.groupby(['grav', 'catv']).sum()
    grav_df['Ratio'] = round((grav_df['Unit'] / grav_df['Unit'].sum())*100, 2)
    figure = px.bar(grav_df, x=grav_df.index.get_level_values(0), y='Ratio', color = grav_df.index.get_level_values(1), text='Ratio')
    figure.update_layout(xaxis_title="Etat", 
                         yaxis_title="Proportion (%)",
                         font=dict(size=18))
    figure.update_yaxes(range=[0, 100])
    return figure

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)

