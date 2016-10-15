import matplotlib.pyplot as plt
import numpy as np

def combine_baseline():
	vms = ['1', '2']
	series_count = 5
	fbase = 'logs/microbench'
	experiments_cnt = 64;
	for i in range(1, series_count + 1):
		response_times = []
		response_times_std = []
		throughputs = []
		for j in range(0, experiments_cnt):
			response_times.append(0)
			response_times_std.append(0)
			throughputs.append(0)

		for vm in vms:
			with open('logs/throughput_' + str(i) + '_' + vm, 'r') as f:
				j = 0
				for line in f:
					throughputs[j] += int(line)
					j+=1
			with open('logs/response_time_' + str(i) + '_' + vm, 'r') as f:
				j = 0
				for line in f:
					line = line.split(' ')
					response_times[j] += int(line[0])
					response_times_std[j] += float(line[1])
					j+=1

		for j in range(0, experiments_cnt):
			response_times[j] /= len(vms)
			response_times_std[j] /= len(vms)

		with open(fbase + str(i) + '.log', 'w+') as f:
			for j in range(0, experiments_cnt):
				f.write(str(throughputs[j]) + ' ' + str(response_times[j]) + ' ' + str(response_times_std[j]) + '\n')

def draw_baseline_plots():
	series_cnt = 5
	experiments_cnt = 64;
	fbase = 'logs/microbench'
	results = [[], [[], []]]
	for i in range(0, experiments_cnt):
		results[0].append([])
		results[1][0].append([])
		results[1][1].append([])
	for i in range(1, series_cnt + 1):
		with open(fbase + str(i) + '.log', 'r') as f:
			j = 0
			for line in f:
				line = line.split(' ')
				results[0][j].append(int(line[0]))
				results[1][0][j].append(float(line[1]))
				results[1][1][j].append(float(line[2]))
				j += 1
	new_results = [[], [[], []]]
	for i in range(0, experiments_cnt):
		new_results[0].append(np.array(results[0][i]))
		new_results[1][0].append(np.array(results[1][0][i]))
		new_results[1][1].append(np.array(results[1][1][i]))

	avgs = [[], []]
	stds = [[], []]
	x = []
	for i in range(0, experiments_cnt):
		avgs[0].append(new_results[0][i].mean())
		avgs[1].append(new_results[1][0][i].mean())
		stds[1].append(new_results[1][1][i].mean())
		print(new_results[0][i].mean())
		x.append((i+1)*2)

	plt.plot(x, avgs[0])
	plt.savefig('baseline_throughput.png')
	plt.clf()

	plt.errorbar(x, avgs[1], stds[1])
	plt.savefig('baseline_response_time.png')


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
