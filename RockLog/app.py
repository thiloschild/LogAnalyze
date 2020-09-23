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
#############
from functions import *


#################################################################################
#Dash
#################################################################################

df = get_df()
sort_df(df)
PAGE_SIZE = 40
lenght_df = len(df.index)
PAGE_COUNT = int(lenght_df/PAGE_SIZE)+1

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

##################################################################################
#Layout
app.layout = html.Div(children=[
    html.H1(children='Logs from The Rock'),

    html.Div(children='''
        
    '''),


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
        page_size=PAGE_SIZE,
        page_count=PAGE_COUNT,
        page_action='custom',

        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='single',
        sort_by=[]),
    
    html.Br(),html.Br(),html.Br(),

    html.Div(html.A(html.Button('Download'),
        id='test',
        download="logs.csv",
        href=""),
    id='download-link'),

    html.Br(),

], style={'marginLeft': 25, 'marginRight': 25, 'marginTop': 15, 'marginBottom': 15})
operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3

##################################################################################
#App Callback

@app.callback(
    Output('graph', 'figure'),
    [Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])
def update_figure(sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]


    id = dff["id"]
    proteins = dff["proteins"]
    peptides = dff["peptides"]
    analyzed = dff["analyzed"]
    index_list = get_index_list(df)


    fig=go.Figure(
        data=[
            go.Bar(name="Proteins", x=index_list, y=proteins, yaxis='y', offsetgroup=1,
                   text=['<b>%s</b><br>id: %d<br>Proteins: %d<br>Peptides: %d<br>Queries: %d<br>Hits: %d<br>Sample: %s<br>aquired: %s<br>analyzed: %s<br>type: %s<br>msResolution: %s<br>ChromFWHM_Min: %s'%(t,s,r,v,w,q,x,y,z,a,b,c) 
                   for t,s,r,v,w,q,x,y,z,a,b,c in df.loc[:,['name','id','proteins','peptides','queries','hits','sample','aquired','analyzed','type','msResolution','ChromFWHM_Min']].values], hoverinfo = 'text',),
            go.Bar(name='Peptides', x=index_list, y=peptides, yaxis='y2', offsetgroup=2,
                   text=['<b>%s</b><br>id: %d<br>Proteins: %d<br>Peptides: %d<br>Queries: %d<br>Hits: %d<br>Sample: %s<br>aquired: %s<br>analyzed: %s<br>type: %s<br>msResolution: %s<br>ChromFWHM_Min: %s'%(t,s,r,v,w,q,x,y,z,a,b,c) 
                   for t,s,r,v,w,q,x,y,z,a,b,c in df.loc[:,['name','id','proteins','peptides','queries','hits','sample','aquired','analyzed','type','msResolution','ChromFWHM_Min']].values], hoverinfo = 'text',),
        ],
        layout=
            {
             'plot_bgcolor': '#FFF',
             'yaxis': {'title': 'Proteins'},
             'yaxis2': {'title': 'Peptides', 'overlaying': 'y', 'side': 'right'},
             'xaxis': {'title': 'Experiments', 'showticklabels': False}
            }
        )

    fig.update_layout(
        barmode="group",
        hoverlabel=dict(
        bgcolor="white", 
        font_size=16,
        font_family="Rockwell"
        )
    )
    return fig

@app.callback(
    Output('info_graph', 'figure'),
    [Input('dropdown', 'value')])
def update_info_graph(selected_dropdown_value):
    df = get_df()
    figure = px.line(df, x=get_index_list(df), y=selected_dropdown_value)
    return figure

@app.callback(
    Output('table-sorting-filtering', 'data'),
    [Input('table-sorting-filtering', 'page_current'),
     Input('table-sorting-filtering', 'page_size'),
     Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])
def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')

@app.callback(
    dash.dependencies.Output('test', 'href'),
    [dash.dependencies.Input('download-link', 'n_clicks')])
def update_download_link(n_clicks):
    df = get_df()
    csv_string = df.to_csv(index=False, encoding='utf-8')
    csv_string = csv_string.replace(" ", "_")
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string


##################################################################################
#run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
