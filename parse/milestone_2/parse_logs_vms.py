import os
import math
import statistics as st
# import numpy as np

def is_to_move(filename):
	# if (not filename.startswith('max_throughput')):
	# 	return True
	if (not filename.startswith('max_throughput_')):
		return False
	filename = filename.replace('max_throughput_', '')
	filename = filename.replace('.log', '')
	parts = filename.split('_')

	if (int(parts[0]) <= 300) and (int(parts[1]) == 30):
		return False

	# if filename.find('.log') == -1:
	# 	return False
	return True
	# if (int(parts[0]) >= 450) and (int(parts[0]) <= 600) and (int(parts[1]) >= 30):
	# 	return True
	# return False

def move_logs(directory_name):
	directory = './logs/detailed'
	for filename in os.listdir(directory):
		if (not os.path.isdir(os.path.join(directory, filename))) and (is_to_move(filename)):
			os.rename(os.path.join(directory, filename), os.path.join('./logs/%s/' % directory_name, filename))


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

def parse_max_throughput(detailed):
	if detailed:
		directory = './logs/detailed'
	else:
		directory = './logs/overall'
	parse_throughput('max_throughput', ['Number of clients', 'Size of thread pool', 'TPS'], directory)
	parse_response_time('max_throughput', 'max_throughput-response_time',
			['Number of clients', 'Size of thread pool', 'Response time', 'Standard deviation'], directory)

def parse_replication():
	params_header = ['Replication factor', 'Number of servers', 'Repetition']
	parse_throughput('replication', params_header + ['TPS', 'Standard deviation'])
	parse_response_time('replication', 'replication-response_time',
				params_header + ['Response time', 'Standard deviation'])
	for type in ['Get', 'Set']:
		parse_response_time('replication', 'replication-response_time-%s' % type.lower(),
				params_header + ['Response time', 'Standard deviation'], type=type)

def parse_writes():
	params_header = ['Writes percentage', 'Number of servers', 'Replication factor' 'Repetition']
	parse_throughput('writes', params_header + ['TPS', 'Standard deviation'])
	parse_response_time('writes', 'writes-response_time',
			params_header + ['Response time', 'Standard deviation'])
	for type in ['Get', 'Set']:
		parse_response_time('writes', 'writes-response_time-%s' % type.lower(),
				params_header + ['Response time', 'Standard deviation'], type=type)


def get_params(fbase, filename):
	data = filename
	data = data.replace(fbase + '_', '')
	data = data.replace('.log', '')
	data = data.replace('[', '_')
	data = data.replace(']', '')
	data = data.split('_')
	return data

def parse_throughput(fbase, headers, directory='./logs'):
	res = []
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			data = get_params(fbase, filename)
			res.append(data + parse_throughput_single(os.path.join(directory, filename)))
		else:
			continue

	res = [headers] + res
	write_to_file(fbase, res)

start_time = 60
end_time = 120

def parse_throughput_single(fname):
	print(fname)
	till_stability_throughput = 0
	res = []
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		started = False
		while i < len(lines):
			line = lines[i]
			if (line.find('Total Statistics') != -1) and (line.find('Total Statistics (') == -1):
				i += 3
				cur_throughput = int(lines[i].split()[3])
				if started:
					res.append(int(lines[i - 1].split()[3])) # from period
				if lines[i].split()[1] == str(start_time):
					till_stability_throughput = cur_throughput
					started = True
				elif lines[i].split()[1] == str(end_time):
					throughput = cur_throughput
					break
			i += 1
		throughput = (throughput * end_time - till_stability_throughput * start_time) / (end_time - start_time)
		return [str(throughput), str(st.pstdev(res))]

def parse_response_time(fbase, result_name, headers, directory='./logs', type='Total'):
	res = []
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			data = get_params(fbase, filename)
			res.append(data + parse_response_time_single(os.path.join(directory, filename), type))
		else:
			continue
	res = [headers] + res
	write_to_file(result_name, res)

def parse_response_time_single(fname, type):
	print(fname)
	till_stability_average = 0
	till_stability_std= 0
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		while i < len(lines):
			line = lines[i]
			if (line.find('%s Statistics' % type) != -1) and (line.find('%s Statistics (' % type) == -1):
				i += 3
				if lines[i].split()[1] == str(start_time):
					till_stability_average = float(lines[i].split()[8])
					till_stability_std = float(lines[i].split()[9])
				elif lines[i].split()[1] == str(end_time):
					response_time = float(lines[i].split()[8])
					response_time_std = float(lines[i].split()[9])
			if (line.find('Log2 Dist:') != -1) and (lines[i-6].find(type) != -1):
				i += 1
				line = lines[i]
				base = int(line.split()[0][:-1])
				perc = []
				while line.strip():
					line = line.split()[1:]
					for k in range(0, len(line)):
						perc.append(str(2**base))
						perc.append(line[k])
						base += 1
					i += 1
					line = lines[i]

			i += 1
		response_time = (response_time * end_time - till_stability_average * start_time) / (end_time - start_time)
		response_time_std = math.sqrt((math.pow(response_time_std, 2) * end_time 
				- math.pow(till_stability_std, 2) * start_time) / (end_time - start_time))


		return [str(response_time), str(response_time_std)] + perc
