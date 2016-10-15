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

def combine_stability():
	vms = ['1', '2', '3']
	fbase = 'logs/stability_parsed'
	response_times = []
	response_times_std = []
	throughputs = []
	i = 0
	for vm in vms:
		with open(fbase + '_' + vm + '.log', 'r') as f:
			j = 0
			for line in f:
				line = line.split(' ')
				if i == 0:
					throughputs.append(int(line[0]))
					response_times.append(int(line[1]))
					response_times_std.append(float(line[2]))
				else:
					throughputs[j] += int(line[0])
					response_times[j] += int(line[1])
					response_times_std[j] += float(line[2])
				j += 1
		i += 1

	for j in range(0, len(response_times)):
		response_times[j] /= len(vms)
		response_times_std[j] /= len(vms)

	with open(fbase + '.log', 'w+') as f:
		for j in range(0, len(throughputs)):
			f.write(str(throughputs[j]) + ' ' + str(response_times[j]) + ' ' + str(response_times_std[j]) + '\n')

def draw_stability_plots():
	fbase = 'logs/stability_parsed.log'
	results = [[], [[], []]]

	tps = []
	response_times = []
	response_times_std = []
	x = []
	with open(fbase, 'r') as f:
		i = 0
		for line in f:
			line = line.split(' ')
			tps.append(int(line[0]))
			response_times.append(float(line[1]))
			response_times_std.append(float(line[2]))
			x.append((i+1)*10)
			i+=1

	plt.ylim([0, 15000])
	plt.xlim([0, 3600])
	plt.grid(True)
	plt.plot(x, tps)
	plt.savefig('stability_throughput.png')
	plt.clf()

	plt.ylim([0, 50000])
	plt.xlim([0, 3600])
	plt.grid(True)
	plt.errorbar(x, response_times, response_times_std)
	plt.savefig('stability_response_time.png')