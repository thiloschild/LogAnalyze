import json
import pandas as pd
import time

#################################
#
#with open('logs.json', 'r') as data:
#	data = data.read()
#
#logs = json.loads(data)
#
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

#df = get_data('logs.json')
#
#print(df)

def fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

def memoize(func):
    cache = dict()

    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return memoized_func

memoized_fibonacci = memoize(fibonacci)

x = memoized_fibonacci(10)
#x = fibonacci(35)
x = memoized_fibonacci(12)
#x = fibonacci(35)
print(x)