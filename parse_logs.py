def parse_throughput(clients):
	fbase = 'logs/microbench'
	series_number = 1
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

def parse_response_time(clients):
	fbase = 'logs/microbench'
	for i in range(1, clients + 1):
		fname = fbase + str(i) 
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