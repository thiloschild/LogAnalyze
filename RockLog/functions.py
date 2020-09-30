import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import json
import pandas as pd
from urllib.request import Request, urlopen
from urllib.error import URLError
import json
from pathlib import Path
import socket
from collections import namedtuple

#########################################################
#class

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


#####################################################################
#functions

def get_data_mock(file):

    with open(file, 'r') as data:
        data = data.read()

    logs = json.loads(data)

    return logs

def get_data():

    s = Sender('Test', '192.168.1.214')
    logs = s.list_logs()

    return logs

def __get_df():

    #logs = get_data_mock('logs.json')
    logs = get_data()

    df = pd.DataFrame(columns=['id',
                               'name',
                               'sample',
                               'aquired',
                               'proteins',
                               'peptides',
                               'queries',
                               'hits',
                               'type',
                               'analyzed',
                               'msResolution',
                               'ChromFWHM_Min'])
 
    lenghth = len(logs)
    i = 0
    f1 = False
    f2 = False
    while i < lenghth:
        for x in logs[i]:

            if x == "create_params_file:output":
                stats = logs[i][6]
                stats = stats.split(',')
                aquired = stats[3].split('"')
                aquired = aquired[3]
                msResolution = stats[10].split(':')
                msResolution = float(msResolution[2])
                ChromFWHM_Min = stats[7].split(':')
                ChromFWHM_Min = float(ChromFWHM_Min[2])
                f1 = True
            if x == "get_search_stats:output":
                #date
                analyzed = logs[i][0].split('.', 2)
                analyzed = analyzed[0]
                #experiment number
                id = logs[i][2]
                type = logs[i][3]
                #peptides_cnt + proteins_cnt + hits_cnt + queries_cnt
                search_stats = logs[i][6]
                stats = search_stats.split(',', 7)
                peptides = stats[5].split(':', 2)
                peptides = int(peptides[1])
                proteins = stats[6].split(':', 2)
                proteins = proteins[1].split('}',2)
                proteins = int(proteins[0])
                queries = stats[3].split(':', 2)
                queries = int(queries[1])
                hits = stats[4].split(':', 2)
                hits = int(hits[1])
                #acquired_name + sample_description
                name = stats[1].split(':', 2)
                name = name[1].split('"', 3)
                name = name[1]
                sample = stats[2].split(':', 2)
                sample = sample[1].split('"', 3)
                sample = sample[1]
                f2 = True

        if (f1==True) and (f2==True):
            df_temp = pd.DataFrame({'id': [id],
                                    'name': [name],
                                    'sample': [sample],
                                    'aquired': [aquired],
                                    'proteins': [proteins],
                                    'peptides': [peptides],
                                    'queries': [queries],
                                    'hits': [hits],
                                    'type': [type],
                                    'analyzed': [analyzed],
                                    'msResolution': [msResolution],
                                    'ChromFWHM_Min': [ChromFWHM_Min]})
            df = pd.concat([df, df_temp])
            f1=False
            f2=False

        i += 1
    
    df = df.reset_index(drop=True)
    return df

class refresh_cache(object):
    def __init__(self, foo):
        self.output = None
        self.foo = foo

    def __call__(self, refresh=False, *args, **kwds):
        if self.output is None or refresh:
            self.output = self.foo(*args, **kwds)
        return self.output

mem_get_df = refresh_cache(__get_df)

def sort_df(df):
    df = df.sort_values(by=['analyzed'])
    df = df.reset_index(drop=True)
    return df

def get_index_list(df):
    index_list = list(df.index.values)
    return index_list

def split_filter_part(filter_part):

    operators = [['ge ', '>='],
                ['le ', '<='],
                ['lt ', '<'],
                ['gt ', '>'],
                ['ne ', '!='],
                ['eq ', '='],
                ['contains '],
                ['datestartswith ']]
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

def filter_data(df, filter):

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

    return dff

def get_page_count(df, PAGE_SIZE):

    lenght_df = len(df.index)
    PAGE_COUNT = int(lenght_df/PAGE_SIZE)+1

    return PAGE_COUNT
