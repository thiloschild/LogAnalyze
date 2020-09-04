import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
#import easygui




from urllib.request import Request, urlopen
from urllib.error import URLError
import json
from pathlib import Path
import socket

from collections import namedtuple

class Sender(object):
    def __init__(self,
                 name,
                 host='192.168.1.214',
                 port=8745, 
                 encoding="cp1251"):
        self.host = host
        self.port = port
        self.encoding = encoding
        self.name = name
        self.ip = socket.gethostbyname(socket.gethostname())
        self.project_id = self.__get_project_id()
        self.group = name

    def __sock(self, route, message=None):
        url = f"http://{self.host}:{self.port}/{route}"
        request = Request(url)
        request.add_header('Content-Type', 'application/json; charset=utf-8')
        if message is None:
            message = json.dumps(self.name).encode(self.encoding)
        return urlopen(request, message)

    def __get_project_id(self):
        with self.__sock('get_project_id') as s:
            return json.loads(s.read())

    def log(self, key, value):
        """Log key-value.
        
        Args:
            key (str): Parameter name.
            value (obj): Any serializable object.
        Returns:
            boolean: success?
        """
        _log = json.dumps((self.ip, 
                           self.project_id,
                           self.name,
                           self.group,
                           key, 
                           dump2json(value))).encode(self.encoding)
        with self.__sock('log', _log) as s:
            return json.loads(s.read())            

    def update_group(self, group):
        self.group = dump2json(group) # general.

    def list_logs(self):

        LOG = namedtuple('log', 'date ip project_id group process_name key value')
        with self.__sock('get_all_logs') as s:
            return [LOG(*log) for log in json.loads(s.read())]

#functions

def get_data(file):

	#with open(file, 'r') as data:
	#	data = data.read()

	#logs = json.loads(data)

	s = Sender('Test', '192.168.1.214')
	logs = s.list_logs()


	df = pd.DataFrame(columns=['exp_num', 'date', 'peptides_cnt', 'proteins_cnt', 'queries_cnt', 'hits_cnt', 'acquired_name', 'sample_description'])


	lenghth = len(logs)
	i = 0
	while i < lenghth:
		for x in logs[i]:
			if x == "get_search_stats:output":
				#date
				date = logs[i][0]
				#experiment number
				exp_num = logs[i][2]
				#peptides_cnt + proteins_cnt + hits_cnt + queries_cnt
				search_stats = logs[i][6]
				stats = search_stats.split(',', 7)
				peptides_cnt = stats[5].split(':', 2)
				peptides_cnt = int(peptides_cnt[1])
				proteins_cnt = stats[6].split(':', 2)
				proteins_cnt = proteins_cnt[1].split('}',2)
				proteins_cnt = int(proteins_cnt[0])
				queries_cnt = stats[3].split(':', 2)
				queries_cnt = int(queries_cnt[1])
				hits_cnt = stats[4].split(':', 2)
				hits_cnt = int(hits_cnt[1])
				#acquired_name + sample_description
				acquired_name = stats[1].split(':', 2)
				acquired_name = acquired_name[1].split('"', 3)
				acquired_name = acquired_name[1]
				sample_description = stats[2].split(':', 2)
				sample_description = sample_description[1].split('"', 3)
				sample_description = sample_description[1]

				df_temp = pd.DataFrame({'exp_num': [exp_num],
										'date': [date],
										'peptides_cnt': [peptides_cnt],
										'proteins_cnt': [proteins_cnt],
										'queries_cnt': [queries_cnt],
										'hits_cnt': [hits_cnt],
										'acquired_name': [acquired_name],
										'sample_description': [sample_description]})
				df = pd.concat([df, df_temp])
		i += 1
	
	df = df.reset_index(drop=True)
	return df

#def save(df):
#	save_path = easygui.filesavebox(default="logs")
#	df.to_excel(save_path+".xlsx")


#################################################################################
#Dash
#################################################################################

df = get_data('logs.json')
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
            {'label': 'Number of Peptides', 'value': 'peptides_cnt'},
            {'label': 'Number of Proteins', 'value': 'proteins_cnt'}
        ],
        value='proteins_cnt'
    ),

    dcc.Graph(id='graph'),

    html.Button(id='button', n_clicks=0, children='Save Logs'),
    html.Div(id='output-container-button', children='Press "SAVE LOGS" to save the logs as xlsx'),

    html.Br(),html.Br(),
    html.H4('Log: '),
    html.Br(),

    dash_table.DataTable(
    	id='table-sorting-filtering',
    	columns=[{"name": i, "id": i} for i in df.columns],
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
	[Input('choose', 'value')])
def update_figure(selected_box):
	df = get_data('logs.json')
	fig = px.bar(df, x="exp_num",
					 y=selected_box,
					 hover_name="acquired_name",
					 hover_data= ['peptides_cnt', 'proteins_cnt', 'date', 'sample_description', 'hits_cnt', 'queries_cnt'])
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
