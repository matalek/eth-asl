import matplotlib.pyplot as plt
import numpy as np
from parse.milestone_2.parse_logs_vms import *

def combine_max_throughput():
	fbase = 'logs_working/max_throughput'
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
	plt.savefig(plot_file_name)
	plt.clf()

def plot_max_throughput_all():
	min_threads = 10
	max_threads = 60
	step_threads = 10
	min_clients = 100
	max_clients = 500
	step_clients = 10
	for clients in range(min_clients, max_clients + 1, step_clients):
		plot_max_throughput(0, clients)
	for threads in range(min_threads, max_threads + 1, step_threads):
		plot_max_throughput(1, threads)

def plot_max_throughput_global():
	min_threads = 10
	max_threads = 60
	step_threads = 10
	min_clients = 100
	max_clients = 500
	step_clients = 10
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

	for threads in range(0, (max_threads - min_threads) // step_threads):
		plt.plot(x, y[threads])
	plt.grid(True)

	plt.title(plot_title_name)
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Clients')
	plt.ylim([0, 42000])
	plt.savefig(plot_file_name)
	plt.clf()
