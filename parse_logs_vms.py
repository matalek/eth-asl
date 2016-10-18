def parse_baseline_throughput(clients, vm_number, series_number = 1):
	fbase = 'logs/microbench'
	res = []
	for i in range(1, clients + 1):
		fname = fbase + str(i) + '_' + str(series_number) 
		with open(fname, 'r') as fh:
			for line in fh:
			    pass
			last = line
			pat = 'TPS: '
			start = last.find(pat) + len(pat)
			end = line[start:].find(' ')
			res.append([str(i), line[start:start+end]])
	res = [['Number of clients', 'TPS']] + res
	write_to_file('throughput', vm_number, series_number, res);

def parse_baseline_response_time(clients, vm_number, series_number = 1):
	fbase = 'logs/microbench'
	res = []
	for i in range(1, clients + 1):
		fname = fbase + str(i) + '_' + str(series_number) 
		with open(fname, 'r') as fh:
			lines = fh.readlines()
			for i in range(0, len(lines)):
				line = lines[i]
				if line.find('Total Statistics (') != -1:
					i += 3
					line = lines[i]
					line = line.replace('Avg:', '')
					line = line.replace(' ', '') 
					avg = line.replace('\n', '')

					i += 2
					line = lines[i]
					line = line.replace('Std:', '')
					line = line.replace(' ', '') 
					line = line.replace('\n', '')
					res.append([str(i), avg, line])
					break
				i += 1
	res = [['Number of clients', 'Response time', 'Response time standard deviation']] + res
	write_to_file('response_time', vm_number, series_number, res);

def write_to_file(name_start, vm_number, series_number, content):
	fres = 'logs/' + name_start + '_' + str(series_number) + '_' + vm_number
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

def parse_baseline(clients, vm_number):
	series_cnt = 5
	for i in range(1, series_cnt + 1):
		parse_baseline_throughput(clients, vm_number, i)
		parse_baseline_response_time(clients, vm_number, i)

def parse_stability(vm_number):
	fname = 'logs/stability.log'
	data = []
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		time = 1
		while i < len(lines):
			line = lines[i]
			if line.find('Total Statistics') != -1:
				if line.find('Total Statistics (') == -1:
					i += 2
					line = lines[i].split()
					data.append([str(time * 10), line[3], line[8], line[9]])
					time += 1
				else:
					# Total average response time and std
					i += 3
					response_time = lines[i].split()[1]
					i += 1
					response_time_std = lines[i].split()[1]
			i += 1
	# For whole experiment
	pat = 'TPS: '
	start = line.find(pat) + len(pat)
	end = line[start:].find(' ')
	tps = line[start:start+end]
	data.append(['Total', tps, response_time, response_time_std])
	data = [['Time', 'TPS', 'Response time', 'Response time standard deviation']] + data
	write_to_named_file('logs/stability_parsed_%d.log' % vm_number, data)
