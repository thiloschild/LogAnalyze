import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
#############
from functions import *


#################################################################################
#Dash
#################################################################################

df = get_df()
PAGE_SIZE = 25
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

    html.H4('Plot:'),
    html.Br(),

    dcc.RadioItems(
    	id='choose',
        options=[
            {'label': 'Number of Peptides', 'value': 'peptides'},
            {'label': 'Number of Proteins', 'value': 'proteins'}
        ],
        value='proteins'
    ),

    dcc.Graph(id='graph'),

    html.Button(id='button', n_clicks=0, children='Save Logs'),
    html.Div(id='output-container-button', children='Press "SAVE LOGS" to save the logs as xlsx'),

    html.Br(),html.Br(),
    html.H4('Log: '),
    html.Br(),

    dash_table.DataTable(
        id='table-sorting-filtering',
        columns=[
            {'name': 'id', 'id': 'íd', 'type': 'numeric'},
            {'name': 'name', 'id': 'name', 'type': 'text'},
            {'name': 'sample', 'id': 'sample', 'type': 'text'},
            {'name': 'aquired', 'id': 'aquired', 'type': 'datetime'},
            {'name': 'proteins', 'id': 'proteins', 'type': 'numeric'},
            {'name': 'peptides', 'id': 'peptides', 'type': 'numeric'},
            {'name': 'queries', 'id': 'queries', 'type': 'numeric'},
            {'name': 'hits', 'id': 'hits', 'type': 'numeric'},
            {'name': 'analyzed', 'id': 'analyzed', 'type': 'datetime'},   
            
        ],
        
        page_current=0,
        page_size=PAGE_SIZE,
        page_count=PAGE_COUNT,
        page_action='custom',

        filter_action='custom',
        filter_query='',

        sort_action='custom',
        sort_mode='single',
        sort_by=[])
])

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
    [Input('choose', 'value'),
     Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])
def update_figure(selected_box, sort_by, filter):
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

    fig = px.bar(dff, x="id",
                      y=selected_box,
                      hover_name="name",
                      hover_data= ['peptides', 'proteins', 'queries', 'hits', 'sample', 'aquired', 'analyzed'])
    fig.update_layout(
        hoverlabel=dict(
        bgcolor="white", 
        font_size=16, 
        font_family="Rockwell"
        )
    )
    return fig


@app.callback(
	Output('output-container-button', 'children'),
	[Input('button', 'n_clicks')])
def run_on_click(n_clicks):
	if not n_clicks:
		raise PreventUpdate

	df = get_data('logs.json')
	#save(df)
	return 'The file as been saved!'


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
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
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


##################################################################################
#run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
