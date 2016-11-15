import numpy as np
from parse.milestone_2.parse_logs_vms import *

repetitions = 3
stats_cnt = 3

def parse_middleware_times(fbase, type, headers, repetition=0):
	res = []
	directory = './logs'
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			temp = filename.replace('.log', '')
			if repetition != 0:
				if (temp[-1] != ']') or (int(temp[-2]) != repetition):
					continue
				temp = temp[:-3]
			data = get_params(fbase, temp)
			res.append(data + parse_middleware_times_single(os.path.join(directory, filename), type))
		else:
			continue
	res.sort()
	res = [headers] + res
	if repetition != 0:
		write_to_file(fbase + '-' + type + '[' + str(repetition) + ']' , res)
	else:
		write_to_file(fbase + '-' + type, res)

def parse_middleware_times_single(fname, type):
	print(fname)
	res = []
	for i in range(0, stats_cnt):
		res.append([])
	with open(fname, 'r') as f:
		lines = f.readlines()
		j = 1
		while j < len(lines):
			line = lines[j].split()
			if (line[1] == type) or (type == 'all'):
				for i in range(0, stats_cnt):
					res[i].append(int(line[2 + i]))
			j += 2
	

	data = []
	for i in range(0, stats_cnt):
		cnt = len(res[i])
		res[i] = res[i][int(cnt / 3):int(2 * cnt / 3)]
		data += [str(np.average(res[i])), str(np.std(res[i]))]
	return data

def combine_repetitions(fbase, params_size=2):
	lines = []
	for rep in range(1, repetitions + 1):
		f = open('logs/' + fbase + '[' + str(rep) + '].log', 'r')
		lines.append(f.readlines())

	lines_cnt = len(lines[0])
	headers = lines[0][0].rstrip()
	res = []

	for i in range(1, lines_cnt):
		values = []
		for j in range(0, stats_cnt * 2):
			values.append(0)
		for rep in range(0, repetitions):
			line = lines[rep][i].split(',')
			params = line[:params_size]
			# params[1] = params[1][:1]
			for j in range(0, stats_cnt * 2):
				values[j] += float(line[params_size + j])
		for j in range(0, stats_cnt * 2):
			values[j] = str(values[j] / repetitions)
		res.append(params + values)

	res = [[headers]] + res
	write_to_file(fbase, res)

# --------- Effect of replication task -------------

def parse_replication_middleware():
	middleware_headers = ['Replication factor', 'Number of servers', 'Middleware time', 'Middleware time std', 
			'Queue time', 'Queue time std', 'Server time', 'Server time std']
	for i in range(1, repetitions + 1):
		parse_middleware_times('replication', 'get', middleware_headers, i)
		parse_middleware_times('replication', 'set', middleware_headers, i)
		
	combine_replication_repetitions()

def combine_replication_repetitions():
	combine_repetitions('replication-get')
	combine_repetitions('replication-set')

# --------- Effect of writes task -------------

def parse_writes_middleware():
	middleware_headers = ['Writes percentage', 'Number of servers', 'Replication factor', 'Middleware time', 'Middleware time std', 
			'Queue time', 'Queue time std', 'Server time', 'Server time std']
	for i in range(1, repetitions + 1):
		parse_middleware_times('writes', 'get', middleware_headers, i)
		parse_middleware_times('writes', 'set', middleware_headers, i)
		parse_middleware_times('writes', 'all', middleware_headers, i)
		
	combine_writes_repetitions()

def combine_writes_repetitions():
	combine_repetitions('writes-get', 3)
	combine_repetitions('writes-set', 3)
	combine_repetitions('writes-all', 3)

