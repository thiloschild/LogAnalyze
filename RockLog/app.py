import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import urllib.parse
from datetime import datetime
#############
from functions import *


#################################################################################
#Dash
#################################################################################

df = mem_get_df()
df = sort_df(df)
now = datetime.now()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##################################################################################
#Layout
app.layout = html.Div(children=[
    html.H1(children='Logs from The Rock'),

    html.Div(children='''
        
    '''),

    html.Br(),html.Br(),
    html.A(html.Button('Refresh', id='refresh_button', n_clicks=0), href='/'),
    html.Div(id='refreshed', children=''),

    dcc.Graph(id='graph'),


    dcc.Dropdown(id='dropdown',
                 options=[
                   {'label': 'msResolution', 'value': 'msResolution'},
                   {'label': 'ChromFWHM_Min', 'value': 'ChromFWHM_Min'}
                 ],
                 value='msResolution'
        ),

    dcc.Graph(id='info_graph',
        config={'displayModeBar': False},
    ),

    html.Br(),

    dash_table.DataTable(
        id='table-sorting-filtering',
        columns=[
            {'name': 'id', 'id': 'id', 'type': 'numeric'},
            {'name': 'name', 'id': 'name', 'type': 'text'},
            {'name': 'sample', 'id': 'sample', 'type': 'text'},
            {'name': 'aquired', 'id': 'aquired', 'type': 'datetime'},
            {'name': 'proteins', 'id': 'proteins', 'type': 'numeric'},
            {'name': 'peptides', 'id': 'peptides', 'type': 'numeric'},
            {'name': 'queries', 'id': 'queries', 'type': 'numeric'},
            {'name': 'hits', 'id': 'hits', 'type': 'numeric'},
            {'name': 'type', 'id': 'type', 'type': 'text'},
            {'name': 'analyzed', 'id': 'analyzed', 'type': 'datetime'},
            {'name': 'msResolution', 'id': 'msResolution', 'type': 'numeric'},
            {'name': 'ChromFWHM_Min', 'id': 'ChromFWHM_Min', 'type': 'numeric'},
            
        ],
        
        page_current=0,
        page_size=40,
        page_action='custom',

        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='single',
        sort_by=[]),
    
    html.Br(),
    'Page size: ',
    dcc.Input(
        id='datatable-page-size',
        type='number',
        min=1,
        value=40
    ),
    html.Br(),html.Br(),

    html.Div(html.A(html.Button('Download'),
        id='test',
        download="logs.csv",
        href=""),
    id='download-link'),

    html.Br(),

], style={'marginLeft': 25, 'marginRight': 25, 'marginTop': 15, 'marginBottom': 15})

##################################################################################
#App Callback

#First Graph
@app.callback(
    Output('graph', 'figure'),
    [Input('table-sorting-filtering', 'filter_query')])
def update_figure(filter):
    df = mem_get_df()
    dff = filter_data(df, filter)

    id = dff["id"]
    proteins = dff["proteins"]
    peptides = dff["peptides"]
    analyzed = dff["analyzed"]
    index_list = get_index_list(df)
###########

##############
    trace0 = go.Bar(name="Proteins", x=index_list, y=proteins, xaxis='x', yaxis='y',
                   text=['<b>%s</b><br>id: %d<br>Proteins: %d<br>Peptides: %d<br>Queries: %d<br>Hits: %d<br>Sample: %s<br>aquired: %s<br>analyzed: %s<br>type: %s<br>msResolution: %s<br>ChromFWHM_Min: %s'%(t,s,r,v,w,q,x,y,z,a,b,c) 
                   for t,s,r,v,w,q,x,y,z,a,b,c in dff.loc[:,['name','id','proteins','peptides','queries','hits','sample','aquired','analyzed','type','msResolution','ChromFWHM_Min']].values], hoverinfo = 'text',)
    
    trace1 =  go.Bar(name='Peptides', x=index_list, y=peptides, xaxis='x2', yaxis='y2',
                   text=['<b>%s</b><br>id: %d<br>Proteins: %d<br>Peptides: %d<br>Queries: %d<br>Hits: %d<br>Sample: %s<br>aquired: %s<br>analyzed: %s<br>type: %s<br>msResolution: %s<br>ChromFWHM_Min: %s'%(t,s,r,v,w,q,x,y,z,a,b,c) 
                   for t,s,r,v,w,q,x,y,z,a,b,c in dff.loc[:,['name','id','proteins','peptides','queries','hits','sample','aquired','analyzed','type','msResolution','ChromFWHM_Min']].values], hoverinfo = 'text',)

    fig = make_subplots(rows = 2,
                        cols = 1,
                        subplot_titles = ("Proteins", "Peptides"),
                        shared_xaxes = True)

    fig.append_trace(trace0, 1, 1)
    fig.append_trace(trace1, 2, 1)


########
    fig.update_layout(
        height = 800,
        hoverlabel=dict(
            bgcolor="white", 
            font_size=16,
            font_family="Rockwell"
        )
    )
    fig.update_xaxes(showticklabels=False)
    return fig

#Second Graph
@app.callback(
    Output('info_graph', 'figure'),
    [Input('dropdown', 'value'),
     Input('table-sorting-filtering', 'filter_query')])
def update_info_graph(selected_dropdown_value, filter):
    df = mem_get_df()
    dff = filter_data(df, filter)
    dff = sort_df(dff)
    selected_dropdown_value = dff[selected_dropdown_value]

    fig = px.line(dff, x=get_index_list(dff), y=selected_dropdown_value)

    fig.update_layout(xaxis_title="Experiments")
    fig.update_xaxes(showticklabels=False)

    return fig

#Table
@app.callback(
    Output('table-sorting-filtering', 'data'),
    [Input('table-sorting-filtering', 'page_current'),
     Input('table-sorting-filtering', 'page_size'),
     Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])
def update_table(page_current, page_size, sort_by, filter):
    df = mem_get_df()
    dff = filter_data(df, filter)
    dff = dff.sort_values(by=['id'], ascending=False) #default sorting by id -> descending
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'desc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')

#Table - update page count
@app.callback(
    Output('table-sorting-filtering', 'page_count'),
    [Input('table-sorting-filtering', 'page_current'),
     Input('table-sorting-filtering', 'page_size'),
     Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])
def update_table_page_count(page_current, page_size, sort_by, filter):
    dff = filter_data(df, filter)
    page = page_current
    size = page_size
    page_count = get_page_count(dff, size)
    return page_count

#Table - update page size
@app.callback(
    Output('table-sorting-filtering', 'page_size'),
    [Input('datatable-page-size', 'value')])
def update_table_page_size(page_size):
    if page_size != None:
        return page_size
    else:
        return 1

#Download
@app.callback(
    dash.dependencies.Output('test', 'href'),
    [dash.dependencies.Input('download-link', 'n_clicks')])
def update_download_link(n_clicks):
    df = mem_get_df(refresh=True)
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = csv_string.replace(" ", "_")
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

#Refresh Button
@app.callback(
    dash.dependencies.Output('refreshed', 'children'),
    [dash.dependencies.Input('refresh_button', 'n_clicks')])
def update_download_link(n_clicks):
    df = mem_get_df(refresh=True)
    now = datetime.now()
    msg = 'Refreshed on: {}'.format(now.strftime("%d/%m/%Y %H:%M:%S"))
    return msg
##################################################################################
#run the app

def main():
    app.run_server(debug=True, port=8050)

if __name__ == '__main__':
    main()