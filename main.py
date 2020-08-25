import json
import pandas as pd

################################

with open('logs.json', 'r') as data:
	data = data.read()

logs = json.loads(data)

########################

def get_data(file):

	with open(file, 'r') as data:
		data = data.read()

	logs = json.loads(data)

	#s = Sender('Test', '192.168.1.214')
	#logs = s.list_logs()


	df = pd.DataFrame(columns=['exp_num', 'date', 'peptides_cnt', 'proteins_cnt', 'queries_cnt', 'hits_cnt', 'acquired_name', 'sample_description'])


	lenghth = len(logs)
	i = 0
	while i < lenghth:
		for x in logs[i]:
			if x == "get_search_stats:output":
				#print(logs[i])
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
				acquired_name = acquired_name[1]
				sample_description = stats[2].split(':', 2)
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

	



df = get_data('logs.json')

print(df[1:130])