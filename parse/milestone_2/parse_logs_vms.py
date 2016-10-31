import os

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
			if (int(data[1]) >= 10) or (int(data[1]) == 20) or (int(data[0]) > 700):
				continue
			res.append(data + parse_throughput_single(os.path.join(directory, filename)))
		else:
			continue

	res = [headers] + res
	write_to_file(fbase, res)

stability_time = 30 

def parse_throughput_single(fname):
	till_stability_throughput = 0
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		while i < len(lines):
			line = lines[i]
			if (line.find('Total Statistics') != -1) and (line.find('Total Statistics (') == -1):
				i += 2
				if till_stability_throughput == 0:
					till_stability_throughput = int(lines[i].split()[3])
			i += 1
		last = line
		print(fname)
		pat = 'TPS: '
		start = last.find(pat) + len(pat)
		end = line[start:].find(' ')
		throughput = int(line[start:start+end])
		throughput = (4 * throughput - till_stability_throughput)/3
		return [str(throughput)]

def parse_response_time(fbase, result_name, headers):
	res = []
	directory = './logs'
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			data = get_params(fbase, filename)
			res.append(data + parse_response_time_single(os.path.join(directory, filename)))
		else:
			continue
	res = [headers] + res
	write_to_file(result_name, res)

def parse_response_time_single(fname):
	till_stability_average = 0
	till_stability_deviation = 0
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		while i < len(lines):
			line = lines[i]
			if line.find('Total Statistics') != -1:
				if line.find('Total Statistics (') == -1:
					i += 2
					if till_stability_average == 0:
						till_stability_average = int(lines[i].split()[8])
						till_stability_deviation = int(lines[i].split()[9])
				else: # total global
					i += 3
					response_time = lines[i].split()[1]
					i += 1
					response_time_std = lines[i].split()[1]
					break
			i += 1
		last = line
		pat = 'time: '
		start = last.find(pat) + len(pat)
		end = line[start:].find('s')
		run_time = float(line[start:start+end])
		# response_time = 
		return [str(response_time), str(response_time_std)]