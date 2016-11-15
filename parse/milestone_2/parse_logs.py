import matplotlib.pyplot as plt
import numpy as np
from parse.milestone_2.parse_logs_vms import *
import math

# --------- Combining ------------- 

def combine_throughput(fbase, servers=5, rep=False):
	combine(fbase, True, servers, rep)

def combine_response_time(fbase, servers=5, rep=False):
	combine(fbase, False, servers, rep)

def combine(fbase, is_throughput, servers, rep):
	res = {}
	cnts = {}
	for i in range(1, servers + 1):
		with open(fbase + '_' + str(i) + '.log', 'r') as f:
			next(f)
			for line in f:
				values = line.split(',')
				if rep:
					key = values[0] + ',' + values[1] + ',' + values[2]
					offset = 3
				else:
					key = values[0] + ',' + values[1]
					offset = 2
				[value, std] = res.get(key, [0, 0])
				cnt = cnts.get(key, 0)
				value += float(values[offset])
				std += math.pow(float(values[offset + 1]), 2)
				res[key] = [value, std]
				cnts[key] = cnt + 1

	data = []
	max_value = 0
	for key, values in res.items():
		new_key = key.split(',')
		if (servers == 5) and (len(new_key[0]) < 3):
			new_key[0] = '0' + new_key[0]
		if is_throughput:
			value = values[0]
			if value > max_value:
				max_value = value
				max_key = key
		else:
			value = values[0] / cnts[key]
		std = math.sqrt(values[1])
		data.append(new_key + [str(value), str(std)])
	data.sort()

	if is_throughput:
		print(max_key, max_value)

	res_file_name = fbase
	if rep:
		res_file_name += '-rep'

	write_to_named_file(res_file_name + '.log', data)

def combine_vms_repetitions(fbase):
	f = open('./logs_working/' + fbase + '-rep.log', 'r')
	res = {}
	cnts = {}
	for line in f:
		values = line.split(',')
		key = values[0] + ',' + values[1]
		[value, std] = res.get(key, [0, 0])
		cnt = cnts.get(key, 0)
		value += float(values[3])
		std += float(values[4])
		res[key] = [value, std]
		cnts[key] = cnt + 1

	data = []
	max_value = 0
	for key, values in res.items():
		new_key = key.split(',')
		value = values[0] / cnts[key]
		std = values[1] / cnts[key]
		data.append(new_key + [str(value), str(std)])
	data.sort()
	write_to_named_file('./logs_working/' + fbase + '.log', data)

# --------- Middleware logs -------------
def parse_middleware_logs(fname, type):
	stats_cnt = 4
	res = []
	for i in range(0, stats_cnt):
		res.append([])
	with open(fname, 'r') as f:
		lines = f.readlines()
		j = 1
		while j < len(lines):
			line = lines[j].split()
			if line[1] == type:
				for i in range(0, stats_cnt):
					res[i].append(int(line[2 + i]))
			j += 2


	for i in range(0, stats_cnt):
		print(str(np.average(res[i])) + ' ' + str(np.std(res[i])) + ' ' + str(np.percentile(res[i], 25)))


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

def plot_max_throughput_response_time(const_type, value):
	value = str(value)
	fname = 'logs_working/max_throughput-response_time.log'
	x = []
	y = []
	std = []
	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			if line[const_type] == value:
				 x.append(int(line[1 - const_type]))
				 y.append(float(line[2]))
				 std.append(float(line[3]))

	plot_title_name = 'Maximum throughput experiment: ' + value
	plot_file_name = 'plots/max_throughput-response_time_' + value + '_';
	if const_type == 0:
		plot_title_name += ' clients'
		plot_file_name += 'clients'
		plot_x_label = 'Threads'
	else:
		plot_title_name += ' threads'
		plot_file_name += 'threads'
		plot_x_label = 'Clients'

	plot_file_name += '.png'

	plt.errorbar(x, y, std)
	plt.grid(True)

	plt.title(plot_title_name)
	plt.ylabel('Response time [us]')
	plt.xlabel(plot_x_label)
	plt.gca().set_ylim(bottom=0)
	plt.savefig(plot_file_name)
	plt.clf()

min_threads = 30
max_threads = 30
step_threads = 10

def plot_max_throughput_all():
	for threads in range(min_threads, max_threads + 1, step_threads):
		plot_max_throughput(1, threads)
		plot_max_throughput_response_time(1, threads)

def plot_max_throughput_global(detailed=False):
	plot_max_throughput_throughput_global(detailed)
	plot_max_throughput_response_time_global(detailed)

def plot_max_throughput_throughput_global(detailed=False):
	if (detailed):
		dir_name = 'detailed'
		min_threads = 30
		max_threads = 30
	else:
		dir_name = 'overall'
		min_threads = 10
		max_threads = 60
	fname = 'logs_working/%s/max_throughput.log' % dir_name
	x = []
	y = []
	std = []
	for threads in range(min_threads, max_threads + 1, step_threads):
		x.append([])
		y.append([])
		std.append([])

	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			clients = int(line[0])
			threads_it = (int(line[1]) - min_threads) // step_threads
			x[threads_it].append(int(clients))
			y[threads_it].append(float(line[2]))
			std[threads_it].append(float(line[3]))

	plot_title_name = 'Maximum throughput experiment'
	plot_file_name = 'plots/max_throughput_all_%s.png' % dir_name

	i = 0
	for threads in range(0, (max_threads - min_threads) // step_threads + 1):
		plt.errorbar(list(map(lambda el: el + i, x[threads])), y[threads], std[threads], label = str(min_threads + threads * step_threads))
		i += 3
	plt.grid(True)
	if not detailed:
		plt.legend(title = 'Threads', bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
		plt.tight_layout(pad=6)

	plt.title(plot_title_name)
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Clients')
	plt.gca().set_ylim(bottom=0)
	plt.savefig(plot_file_name)
	plt.clf()

def plot_max_throughput_response_time_global(detailed=False):
	if (detailed):
		dir_name = 'detailed'
		min_threads = 30
		max_threads = 30
	else:
		dir_name = 'overall'
		min_threads = 10
		max_threads = 60
	fname = 'logs_working/%s/max_throughput-response_time.log' % dir_name
	x = []
	y = []
	std = []

	for threads in range(min_threads, max_threads + 1, step_threads):
		x.append([])
		y.append([])
		std.append([])

	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			clients = int(line[0])
			threads_it = (int(line[1]) - min_threads) // step_threads
			x[threads_it].append(clients) 
			y[threads_it].append(float(line[2]))
			std[threads_it].append(float(line[3]))

	plot_title_name = 'Maximum throughput experiment'
	plot_file_name = 'plots/max_throughput-response_time_all_%s.png' % dir_name

	for threads in range(0, (max_threads - min_threads) // step_threads + 1):
		plt.plot(x[threads], y[threads])		
	plt.grid(True)
	if not detailed:
		plt.legend(title = 'Threads', bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
		plt.tight_layout(pad=6)

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
	plot_replication_general('replication', 'replication', is_time=False)
	plot_replication_general('replication-get', 'replication-get', header_line=True)
	plot_replication_general('replication-set', 'replication-set', header_line=True)
	plot_replication_general('replication-get', 'replication-get-queue', 4, True)
	plot_replication_general('replication-get', 'replication-get-servers', 6, True)
	plot_replication_general('replication-set', 'replication-set-queue', 4, True)
	plot_replication_general('replication-set', 'replication-set-servers', 6, True)

def plot_replication_general(fbase, title, which_params=2, header_line=False, is_time=True):
	print(title)
	fname = 'logs_working/%s.log' % fbase

	print(fname)

	x = replication_factors_values
	y = []
	std = []
	for servers in servers_values:
		y.append([])
		std.append([])

	with open(fname, 'r') as f:
		if header_line:
			next(f)
		for line in f:
			line = line.split(',')
			y[replication_factors_values.index(int(line[0]))].append(float(line[which_params])) # assuming somehow sorted
			std[replication_factors_values.index(int(line[0]))].append(float(line[which_params + 1])) # assuming somehow sorted

	N = 3

	ind = np.arange(N)  # the x locations for the groups
	width = 0.25       # the width of the bars

	fig, ax = plt.subplots()
	rects = []
	i = 0
	colors = ['r', 'g', 'b']
	for replication in replication_factors_values:
		rects.append(
				ax.bar(ind + i * width, y[i], width, color=colors[i], yerr=std[i],
						error_kw=dict(ecolor='purple', lw=1, capsize=2, capthick=2)))
		i += 1


	ax.tick_params(axis='x', which='both', top='off', bottom='off')
	ax.set_xticks(ind + 2 * width - 1/8)
	ax.set_xticklabels(('3', '5', '7'))

	legend = ax.legend((rects[0][0], rects[1][0], rects[2][0]), ('None', 'Half', 'All'), title='Replication factor',
			bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize='small')
	plt.setp(legend.get_title(),fontsize='x-small')
	plt.tight_layout(pad=8)

	plot_title_name = replication_experiment_title
	plot_file_name = 'plots/%s.png' % title 

	plt.subplots_adjust(top=0.9, bottom=0.1)
	plt.grid(True)
	plt.gca().set_ylim(bottom=0)
	plt.title(plot_title_name)
	if is_time:
		plt.ylabel('Time in the middleware [us]')
	else:
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

