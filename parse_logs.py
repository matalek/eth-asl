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
				next(f)
				for line in f:
					line = line.split(',')
					throughputs[j] += int(line[1])
					j+=1
			with open('logs/response_time_' + str(i) + '_' + vm, 'r') as f:
				j = 0
				next(f)
				for line in f:
					line = line.split(',')
					response_times[j] += int(line[1])
					response_times_std[j] += float(line[2])
					j+=1

		for j in range(0, experiments_cnt):
			response_times[j] /= len(vms)
			response_times_std[j] /= len(vms)

		with open(fbase + str(i) + '.log', 'w+') as f:
			f.write('Number of clients,TPS,Response time,Response time standard deviation\n')
			for j in range(0, experiments_cnt):
				f.write(str(2*(j + 1)) + ',' + str(throughputs[j]) + ',' + str(response_times[j]) + ',' + str(response_times_std[j]) + '\n')

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
			next(f)
			for line in f:
				line = line.split(',')
				results[0][j].append(int(line[1]))
				results[1][0][j].append(float(line[2]))
				results[1][1][j].append(float(line[3]))
				j += 1
	new_results = [[], [[], []]]
	for i in range(0, experiments_cnt):
		new_results[0].append(np.array(results[0][i]))
		new_results[1][0].append(np.array(results[1][0][i]))
		new_results[1][1].append(np.array(results[1][1][i]))

	x = []
	avgs = [[], []]
	stds = [[], []]
	for i in range(0, experiments_cnt):
		avgs[0].append(new_results[0][i].mean())
		avgs[1].append(new_results[1][0][i].mean())
		stds[1].append(new_results[1][1][i].mean())
		if (i == 31):
			print(str(avgs[0][-1]) + ',' + str(avgs[1][-1]) + ',' + str(stds[1][-1]))
		x.append((i+1)*2)

	plt.plot(x, avgs[0])
	plt.xlim([0, 128])
	plt.title('Aggregated throughput')
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Time [s]')
	plt.savefig('baseline_throughput.png')
	plt.clf()

	plt.errorbar(x, avgs[1], stds[1])
	plt.xlim([0, 128])
	plt.title('Response time')
	plt.ylabel('Response time [us]')
	plt.xlabel('Time [s]')
	plt.savefig('baseline_response_time.png')

def combine_stability():
	vms = ['1', '2', '3']
	fbase = 'logs/stability_parsed'
	response_times = []
	response_times_std = []
	throughputs = []
	time = []
	i = 0
	for vm in vms:
		with open(fbase + '_' + vm + '.log', 'r') as f:
			j = 0
			next(f)
			for line in f:
				line = line.split(',')
				print(line[3] + '\n')
				if i == 0:
					time.append(line[0])
					throughputs.append(int(line[1]))
					response_times.append(int(line[2]))
					response_times_std.append(float(line[3]))
				else:
					throughputs[j] += int(line[1])
					response_times[j] += int(line[2])
					response_times_std[j] += float(line[3])
				j += 1
		i += 1

	for j in range(0, len(response_times)):
		response_times[j] /= len(vms)
		response_times_std[j] /= len(vms)

	with open(fbase + '.log', 'w+') as f:
		f.write('Time,TPS,Response time,Response time standard deviation\n')
		for j in range(0, len(throughputs)):
			f.write(time[j] +',' + str(throughputs[j]) + ',' + str(response_times[j]) + ',' + str(response_times_std[j]) + '\n')

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def draw_stability_plots():
	fbase = 'logs/stability_parsed.log'
	results = [[], [[], []]]

	tps = []
	response_times = []
	response_times_std = []
	x = []
	with open(fbase, 'r') as f:
		i = 0
		next(f)		
		for line in f:
			line = line.split(',')
			if (RepresentsInt(line[0])):
				x.append(int(line[0]))
			tps.append(int(line[1]))
			response_times.append(float(line[2]))
			response_times_std.append(float(line[3]))
			i+=1

	# Remove last, since it's total data
	total_tps = tps[-1]
	total_response_time = response_times[-1]
	total_response_time_std = response_times_std[-1]
	print(str(total_tps) + ',' + str(total_response_time) + ',' + str(total_response_time_std))
	del tps[-1]
	del response_times[-1]
	del response_times_std[-1]

	plt.ylim([0, 17000])
	plt.xlim([0, 3600])
	plt.grid(True)
	plt.plot(x, tps)
	plt.title('Aggregated throughput')
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Time [s]')
	plt.savefig('stability_throughput.png')
	plt.clf()

	plt.ylim([0, 40000])
	plt.xlim([0, 3600])
	plt.grid(True)
	# plt.errorbar(x, response_times, response_times_std)
	plt.plot(x, response_times)
	response_times_minus = []
	response_times_plus = []
	for i in range(0, len(response_times)):
		response_times_minus.append(response_times[i] - response_times_std[i])
		response_times_plus.append(response_times[i] + response_times_std[i])
	plt.plot(x, response_times_minus)
	plt.plot(x, response_times_plus)
	plt.title('Response time')
	plt.ylabel('Response time [us]')
	plt.xlabel('Time [s]')
	plt.savefig('stability_response_time.png')

def draw_distribution_plot():
	fbase = 'logs/servers_distribution.log'
	results = [[], [], []]
	x = []
	j = 0
	with open(fbase, 'r') as f:
		next(f)
		for line in f:
			line = line.split(',')
			for i in range(0, 3):
				results[i].append(line[i])
			j += 1
			x.append(j * 100000)

	plt.plot(x, results[0])
	plt.plot(x, results[1])
	plt.plot(x, results[2])
	plt.title('Distribution of server load')
	plt.xlabel('Total number of requests')
	plt.ylabel('Number of requests for server')
	plt.savefig('servers_distribution.png')