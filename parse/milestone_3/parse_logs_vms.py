import os
import math
import statistics as st

start_time = 60
end_time = 120

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

headers_response_time_end = ['Response time', 'Standard deviation', 'Bucket distribution (value, size)']

def parse_throughput(fbase, headers, directory='./logs'):
	res = []
	res2 = []
	for filename in os.listdir(directory):
		if filename.startswith(fbase + '_'):
			data = get_params(fbase, filename)
			(stat, general) = parse_throughput_single(os.path.join(directory, filename))
			res.append(data + stat)
			general = list(map(lambda x : str(x), general))
			res2.append(data + general)
		else:
			continue

	res = [headers] + res
	write_to_file(fbase, res)

	# res2 = list(map(lambda x : str(x), res2))
	write_to_file(fbase + '-values', res2)

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

		return ([str(throughput), str(st.pstdev(res))], res)


def parse_response_time_single(fname, type='Total'):
	print(fname)
	till_stability_average = 0
	till_stability_std= 0
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		started = False
		res = []
		while i < len(lines):
			line = lines[i]
			if (line.find('%s Statistics' % type) != -1) and (line.find('%s Statistics (' % type) == -1):
				i += 3
				if started:
					res.append(float(lines[i].split()[9]))
				if lines[i].split()[1] == str(start_time):
					till_stability_average = float(lines[i].split()[8])
					till_stability_std = float(lines[i].split()[9])
					started = True
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

def parse_replication():
	params_header = ['Replication factor', 'Number of servers', 'Repetition']
	parse_throughput('improved-replication', params_header + ['TPS', 'Standard deviation'])
	# parse_response_time('improved-replication', 'improved-replication-response_time',
	# 			params_header + headers_response_time_end)
	# for type in ['Get', 'Set']:
	# 	parse_response_time('improved-replication', 'improved-replication-response_time-%s' % type.lower(),
	# 			params_header + headers_response_time_end, type=type)


def parse_writes():
	params_header = ['Replication factor', 'Number of servers', 'Repetition']
	parse_throughput('improved-writes', params_header + ['TPS', 'Standard deviation'])
	# parse_response_time('improved-writes', 'improved-writes-response_time',
	# 			params_header + headers_response_time_end)
	# for type in ['Get', 'Set']:
	# 	parse_response_time('improved-writes', 'improved-writes-response_time-%s' % type.lower(),
	# 			params_header + headers_response_time_end, type=type)

