def parse(clients):
	fbase = 'logs/microbench'
	for i in range(1, clients + 1):
		fname = fbase + str(i) 
		with open(fname, 'r') as fh:
			for line in fh:
			    pass
			last = line
			pat = 'TPS: '
			start = last.find(pat) + len(pat)
			end = line[start:].find(' ')
			print(line[start:start+end])