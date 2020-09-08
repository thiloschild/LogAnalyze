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


	df = pd.DataFrame(columns=['acquired_time'])


	lenghth = len(logs)
	i = 0
	while i < lenghth:
		for x in logs[i]:
			if x == "create_params_file:output":
				
				stats = logs[i][6]
				stats = stats.split(',')
				acquired_time = stats[3].split('"')
				acquired_time = acquired_time[3]
				print(acquired_time)

				df_temp = pd.DataFrame({'acquired_time': [acquired_time]})
				df = pd.concat([df, df_temp])
		i += 1
	
	df = df.reset_index(drop=True)
	return df



def wirte_logs_to_txt():
	f = open("logs.txt", "a+")
	
	lenghth = len(logs)
	i = 0
	while i < lenghth:
		for x in logs[i]:
			f.write(str(x))
			f.write('\r\n')
		f.write('#################################################### \r\n')
		i += 1
	
	f.close()

df = get_data('logs.json')

print(df)