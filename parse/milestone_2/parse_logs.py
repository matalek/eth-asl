import matplotlib.pyplot as plt
import numpy as np
from parse.milestone_2.parse_logs_vms import *

def combine_throughput(fbase):
	servers = 5
	res = {}
	for i in range(1, servers + 1):
		with open(fbase + '_' + str(i) + '.log', 'r') as f:
			next(f)
			for line in f:
				values = line.split(',')
				key = values[0] + ',' + values[1]
				throughput = res.get(key, 0)
				throughput += float(values[2])
				res[key] = throughput

	data = []
	max_value = 0
	for key, value in res.items():
		key = key.split(',')
		data.append(key + [str(value)])
		if value > max_value:
			max_value = value
			max_key = key
	data.sort()

	print(max_key, max_value)
	write_to_named_file(fbase + '.log', data)

def combine_response_time(fbase):
	servers = 5
	res = {}
	cnts = {}
	for i in range(1, servers + 1):
		with open(fbase + '_' + str(i) + '.log', 'r') as f:
			next(f)
			for line in f:
				values = line.split(',')
				key = values[0] + ',' + values[1]
				response_time = res.get(key, 0)
				cnt = cnts.get(key, 0)
				response_time += float(values[2])
				res[key] = response_time
				cnts[key] = cnt + 1

	data = []
	for key, value in res.items():
		new_key = key.split(',')
		data.append(new_key + [str(value / cnts[key])])
	data.sort()

	write_to_named_file(fbase + '.log', data)

# --------- Max throughput task ------------- 

def plot_max_throughput(const_type, value):
	value = str(value)
	fname = 'logs_working/max_throughput.log'
	x = []
	y = []
	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			if line[const_type] == value:
				 x.append(line[1 - const_type])
				 y.append(line[2])

	plot_title_name = 'Maximum throughput experiment: ' + value
	plot_file_name = 'plots/max_throughput_' + value + '_';
	if const_type == 0:
		plot_title_name += ' clients'
		plot_file_name += 'clients'
		plot_x_label = 'Threads'
	else:
		plot_title_name += ' threads'
		plot_file_name += 'threads'
		plot_x_label = 'Clients'

	plot_file_name += '.png'

	plt.plot(x, y)
	plt.grid(True)

	plt.title(plot_title_name)
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel(plot_x_label)
	plt.gca().set_ylim(bottom=0)
	plt.savefig(plot_file_name)
	plt.clf()

min_threads = 8
max_threads = 8
step_threads = 10
min_clients = 450
max_clients = 700
step_clients = 10

def plot_max_throughput_all():
	for clients in range(min_clients, max_clients + 1, step_clients):
		plot_max_throughput(0, clients)
	for threads in range(min_threads, max_threads + 1, step_threads):
		plot_max_throughput(1, threads)

def plot_max_throughput_global():
	fname = 'logs_working/max_throughput.log'
	x = []
	y = []
	for clients in range(min_clients, max_clients + 1, step_clients):
		x.append(clients)
	for threads in range(min_threads, max_threads + 1, step_threads):
		y.append([])

	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			y[(int(line[1]) - min_threads) // step_threads].append(line[2])

	plot_title_name = 'Maximum throughput experiment'
	plot_file_name = 'plots/max_throughput_all.png'

	for threads in range(0, (max_threads - min_threads) // step_threads + 1):
		plt.plot(x, y[threads])
	plt.grid(True)

	plt.title(plot_title_name)
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Clients')
	plt.gca().set_ylim(bottom=0)
	plt.savefig(plot_file_name)
	plt.clf()

def plot_max_throughput_response_time_global():
	fname = 'logs_working/max_throughput-response_time.log'
	x = []
	y = []
	for clients in range(min_clients, max_clients + 1, step_clients):
		x.append(clients)
	for threads in range(min_threads, max_threads + 1, step_threads):
		y.append([])

	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			y[(int(line[1]) - min_threads) // step_threads].append(line[2])

	plot_title_name = 'Maximum throughput experiment'
	plot_file_name = 'plots/max_throughput-response_time_all.png'

	for threads in range(0, (max_threads - min_threads) // step_threads + 1):
		plt.plot(x, y[threads])
	plt.grid(True)

	plt.title(plot_title_name)
	plt.ylabel('Response time[us]')
	plt.xlabel('Clients')
	plt.gca().set_ylim(bottom=0)
	plt.savefig(plot_file_name)
	plt.clf()

# --------- Effect of replication task -------------

servers_values = [3, 5, 7]
replication_factors_values = [1, 2, 3]

replication_experiment_title = '"Effects of replication" experiment'

def plot_replication():
	plot_replication_general_throughput()
	plot_replication_general_response_time()

def plot_replication_general_throughput():
	fname = 'logs_working/replication-throughput.log'

	x = replication_factors_values
	y = []
	for servers in servers_values:
		y.append([])

	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			y[replication_factors_values.index(int(line[1]))].append(int(line[2])) # assuming somehow sorted

	N = 3

	ind = np.arange(N)  # the x locations for the groups
	width = 0.25       # the width of the bars

	fig, ax = plt.subplots()
	rects = []
	i = 0
	colors = ['r', 'g', 'b']
	for replication in replication_factors_values:
		rects.append(ax.bar(ind + i * width, y[i], width, color=colors[i]))
		i += 1


	ax.set_xticks(ind + 2 * width)
	ax.set_xticklabels(('3', '5', '7'))

	ax.legend((rects[0][0], rects[1][0], rects[2][0]), ('None', 'Half', 'All'), title='Replication factor')

	plot_title_name = replication_experiment_title
	plot_file_name = 'plots/replication_throughput.png' 

	plt.title(plot_title_name)
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Servers')
	plt.savefig(plot_file_name)
	plt.clf()


# --------- Effect of writes task -------------
writes_percentage_factors = [1, 5, 10]
writes_experiment_title = '"Effects of writes" experiment'

def plot_writes_general_throughput():
	fname = 'logs_working/writes-throughput.log'


	for replication in [0, 1]:
		x = writes_percentage_factors
		y = []
		for servers in servers_values:
			y.append([])

		with open(fname, 'r') as f:
			for line in f:
				line = line.split(',')
				if int(line[2]) == replication:
					y[writes_percentage_factors.index(int(line[1]))].append(int(line[3])) # assuming somehow sorted

		N = 3

		ind = np.arange(N)  # the x locations for the groups
		width = 0.25       # the width of the bars

		fig, ax = plt.subplots()
		rects = []
		i = 0
		colors = ['r', 'g', 'b']
		for writes_percentage in writes_percentage_factors:
			rects.append(ax.bar(ind + i * width, y[i], width, color=colors[i]))
			i += 1


		ax.set_xticks(ind + 2 * width)
		ax.set_xticklabels(('3', '5', '7'))

		ax.legend((rects[0][0], rects[1][0], rects[2][0]), ('1%', '5%', '10%'), title='Number of writes')

		plot_title_name = writes_experiment_title + ', ' + ('R = 1' if replication == 0 else 'R = all')
		plot_file_name = 'plots/write_throughput_' + str(replication + 1) + '_replication.png' 

		plt.title(plot_title_name)
		plt.ylabel('Throughput [ops/s]')
		plt.xlabel('Servers')
		plt.savefig(plot_file_name)
		plt.clf()

