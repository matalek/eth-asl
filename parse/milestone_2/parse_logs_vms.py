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
	fbase = 'logs/max_throughput'
	res = []

	directory = './logs'
	for filename in os.listdir(directory):
		if filename.startswith('max_throughput_'):
			data = filename
			data = data.replace('max_throughput_', '')
			data = data.replace('.log', '')
			res.append(data.split('_') + parse_max_throughput_single(os.path.join(directory, filename)))
		else:
			continue

	res = [['Number of clients', 'Size of thread pool', 'TPS']] + res
	write_to_file('max_throughput', res);

def parse_max_throughput_single(fname):
	stability_time = '30'
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
		pat = 'TPS: '
		start = last.find(pat) + len(pat)
		end = line[start:].find(' ')
		throughput = int(line[start:start+end])
		throughput = (4 * throughput - till_stability_throughput)/3
		return [str(throughput)]
