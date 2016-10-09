def parse_baseline_throughput(clients, series_number = 1):
	fbase = 'logs/microbench'
	for i in range(1, clients + 1):
		fname = fbase + str(i) + '_' + str(series_number) 
		with open(fname, 'r') as fh:
			for line in fh:
			    pass
			last = line
			pat = 'TPS: '
			start = last.find(pat) + len(pat)
			end = line[start:].find(' ')
			print(line[start:start+end])

def parse_baseline_response_time(clients, series_number = 1):
	fbase = 'logs/microbench'
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
					line = line.replace(' ', ''); 
					line = line.replace('\n', ''); 
					print(line)
					break
				i += 1

def parse_stability():
	fname = 'logs/stability.log'
	tps = []
	response_times = []
	with open(fname, 'r') as fh:
		lines = fh.readlines()
		i = 0
		while i < len(lines):
			line = lines[i]
			if line.find('Total Statistics') != -1 and line.find('Total Statistics (') == -1:
				i += 2
				line = lines[i].split()
				tps.append(line[3])
				response_times.append(line[8])
			i += 1
	for t in tps:
		print(t)
	print()
	for t in response_times:
		print(t)
