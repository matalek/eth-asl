import os
import math

def is_old(filename):
	if filename.startswith('old'):
		return False
	if (not filename.startswith('max_throughput')):
		return True
	if (not filename.startswith('max_throughput_')):
		return False
	filename = filename.replace('max_throughput_', '')
	filename = filename.replace('.log', '')
	parts = filename.split('_')
	if (int(parts[0]) >= 500) and (int(parts[0]) <= 600) and ((int(parts[1]) % 10) == 0):
		return False
	return True

def move_old_files():
	directory = './logs'
	for filename in os.listdir(directory):
		if is_old(filename):
			# print(os.path.join(directory, filename))
			# print(os.path.join('./logs/old/', filename))
			os.rename(os.path.join(directory, filename), os.path.join('./logs/old/', filename))


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

def parse_max_throughput():
	parse_throughput('max_throughput', ['Number of clients', 'Size of thread pool', 'TPS'])
	parse_response_time('max_throughput', 'max_throughput-response_time',
			['Number of clients', 'Size of thread pool', 'Response time', 'Standard deviation'])

def parse_response():
	parse_throughput('replication', ['Replcation factor', 'Number of servers', 'TPS'])

def get_params(fbase, filename):
	data = filename
	data = data.replace(fbase + '_', '')
	data = data.replace('.log', '')
	data = data.split('_')
	return data

def parse_throughput(fbase, headers):
	res = []
	directory = './logs'
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			data = get_params(fbase, filename)
			if (int(data[1]) == 20) or (int(data[0]) == 600):
				continue
			res.append(data + parse_throughput_single(os.path.join(directory, filename)))
		else:
			continue

	res = [headers] + res
	write_to_file(fbase, res)

stability_time = 30
start_time = 120
end_time = 180

def parse_throughput_single(fname):
	print(fname)
	till_stability_throughput = 0
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		while i < len(lines):
			line = lines[i]
			if (line.find('Total Statistics') != -1) and (line.find('Total Statistics (') == -1):
				i += 3
				if lines[i].split()[1] == str(start_time):
					till_stability_throughput = int(lines[i].split()[3])
				elif lines[i].split()[1] == str(end_time):
					throughput = int(lines[i].split()[3])
					break
			i += 1
		throughput = (throughput * end_time - till_stability_throughput * start_time) / (end_time - start_time)
		return [str(throughput)]

def parse_response_time(fbase, result_name, headers):
	res = []
	directory = './logs'
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			data = get_params(fbase, filename)
			if (int(data[1]) == 20) or (int(data[0]) == 600):
				continue
			res.append(data + parse_response_time_single(os.path.join(directory, filename)))
		else:
			continue
	res = [headers] + res
	write_to_file(result_name, res)

def parse_response_time_single(fname):
	print(fname)
	till_stability_average = 0
	till_stability_std= 0
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		while i < len(lines):
			line = lines[i]
			if (line.find('Total Statistics') != -1) and (line.find('Total Statistics (') == -1):
				i += 3
				if lines[i].split()[1] == str(start_time):
					till_stability_average = float(lines[i].split()[8])
					till_stability_std = float(lines[i].split()[9])
				elif lines[i].split()[1] == str(end_time):
					response_time = float(lines[i].split()[8])
					response_time_std = float(lines[i].split()[9])
					break
			i += 1
		response_time = (response_time * end_time - till_stability_average * start_time) / (end_time - start_time)
		response_time_std = math.sqrt((math.pow(response_time_std, 2) * end_time 
				- math.pow(till_stability_std, 2) * start_time) / (end_time - start_time))
		return [str(response_time), str(response_time_std)]
