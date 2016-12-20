import numpy as np
import os
import math
import statistics as st

stats_cnt = 4
times_cnt = 6

# per_values = [25, 50, 90]
per_values = [25, 50, 90]

time_measured = 3
repetitions = 3

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
	times = []
	for i in range(0, stats_cnt + 1):
		res.append([])
	for i in range(0, times_cnt):
		times.append([])

	numbers = []
	with open(fname, 'r') as f:
		lines = f.readlines()
		j = 1
		while j < len(lines):
			line = lines[j].split()
			if (line[1] == type) or (type == 'all'):
				for i in range(0, stats_cnt):
					res[i].append(int(line[2 + i]))
				# res[stats_cnt].append(int(line[2 + stats_cnt + 1 + 5]) - int(line[2 + stats_cnt + 1 + 2]))
				# for i in range(0, times_cnt):
				# 	times[i].append(int(line[2 + stats_cnt + 1 + i]))
				# print(int(line[2 + stats_cnt + 1]))
				numbers.append(int(line[2 + stats_cnt + 1]))
				# print(numbers[-1])
			j += 2


	data = []
	for i in range(0, stats_cnt):
		cnt = len(res[i])
		res[i] = res[i][int(cnt / time_measured):int((time_measured - 1) * cnt / time_measured)]
		data += [str(np.average(res[i])), str(np.std(res[i]))]
		for p in per_values:
			data.append(str(np.percentile(res[i], p)))

	# number = 0
	# for i in range(0, times_cnt):
	# 	times[i] = times[i][int(cnt / 5):int(4 * cnt / 5)]

	cnt = len(numbers)
	numbers = numbers[int(cnt / time_measured):int((time_measured - 1)  * cnt / time_measured)]

	# i = 0
	# start_time = times[3][i]
	# start_i = i
	# numbers = []
	# while i < len(times[3]):

	# 	if times[3][i] > start_time + service_time:
	# 		numbers.append((i - start_i) * 5)
	# 		start_time = times[3][i]
	# 		start_i = i
	# 	i += 1
	# print(np.average(numbers))
	# print(np.std(numbers))

	data += [str(np.average(numbers))]

	return data

def get_params(fbase, filename):
	data = filename
	data = data.replace(fbase + '_', '')
	data = data.replace('.log', '')
	data = data.replace('[', '_')
	data = data.replace(']', '')
	data = data.split('_')
	return data

def write_to_file(name, content):
	fres = 'logs/' + name + '.log'
	write_to_named_file(fres, content)

def write_to_named_file(fname, content):
	with open(fname, 'w+') as f:
		for val in content:
			i = 0
			for el in val:
				f.write(el)
				i += 1
				if i != len(val):
					f.write(',')
			f.write('\n')


def combine_repetitions(fbase, params_size=2):
	lines = []
	for rep in range(1, repetitions + 1):
		f = open('logs/' + fbase + '[' + str(rep) + '].log', 'r')
		lines.append(f.readlines())

	lines_cnt = len(lines[0])
	headers = lines[0][0].rstrip()
	res = []

	total_stats_cnt = stats_cnt * (2 + len(per_values)) + 1
	for i in range(1, lines_cnt):
		values = []
		for j in range(0, total_stats_cnt):
			values.append(0)
		for rep in range(0, repetitions):
			line = lines[rep][i].split(',')
			params = line[:params_size]
			# params[1] = params[1][:1]
			for j in range(0, total_stats_cnt):
				values[j] += float(line[params_size + j])
				# print(line[params_size + j])
			# print('------')
			# print(values[total_stats_cnt - 1])
		for j in range(0, total_stats_cnt):
			values[j] = str(values[j] / repetitions)
		res.append(params + values)

	res = [[headers]] + res
	write_to_file(fbase, res)

def stats_headers():
	base = ['Middleware time', 'Queue time', 'Servers time']
	ending = ['', ' std']
	for p in per_values:
		ending.append(' ' + str(p) + 'th percentile')
	res = []
	for b in base:
		for e in ending:
			res.append(b + e)
	return res + ['Requests on the fly']

# --------- Effect of replication task -------------

def parse_replication_middleware():
	middleware_headers = ['Replication factor', 'Number of servers'] + stats_headers()
	for i in range(1, repetitions + 1):
		parse_middleware_times('improved-replication', 'get', middleware_headers, i)
		parse_middleware_times('improved-replication', 'set', middleware_headers, i)
		parse_middleware_times('improved-replication', 'all', middleware_headers, i)

	combine_replication_repetitions()

def combine_replication_repetitions():
	combine_repetitions('improved-replication-get')
	combine_repetitions('improved-replication-set')
	combine_repetitions('improved-replication-all')

# --------- Effect of writes task -------------

def parse_writes_middleware():
	middleware_headers = ['Writes percentage', 'Number of servers', 'Replication factor'] + stats_headers()
	for i in range(1, repetitions + 1):
		parse_middleware_times('improved-writes', 'get', middleware_headers, i)
		parse_middleware_times('improved-writes', 'set', middleware_headers, i)
		parse_middleware_times('improved-writes', 'all', middleware_headers, i)

	combine_writes_repetitions()

def combine_writes_repetitions():
	combine_repetitions('improved-writes-get', params_size=3)
	combine_repetitions('improved-writes-set', params_size=3)
	combine_repetitions('improved-writes-all', params_size=3)