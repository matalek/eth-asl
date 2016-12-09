import os
import math
import statistics as st

start_time = 60
end_time = 1740

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
