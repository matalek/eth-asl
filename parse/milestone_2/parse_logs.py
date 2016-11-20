import matplotlib.pyplot as plt
import numpy as np
from parse.milestone_2.parse_logs_vms import *
import math

colors_6 = ['b', 'g', 'r', 'c', 'm', 'y']

# --------- Combining ------------- 

per_values = [25, 90]

def combine_throughput(fbase, servers=5, params_size=2, rep=False):
	combine(fbase, True, servers, params_size, rep)

def combine_response_time(fbase, servers=5, params_size=2, rep=False):
	combine(fbase, False, servers, params_size, rep)

def combine(fbase, is_throughput, servers, params_size=2, rep=False):
	res = {}
	cnts = {}
	stats = {}
	for i in range(1, servers + 1):
		with open(fbase + '_' + str(i) + '.log', 'r') as f:
			next(f)
			for line in f:
				values = line.split(',')
				key = ','.join(values[:params_size])
				[value, std] = res.get(key, [0, 0])
				cnt = cnts.get(key, 0)
				value += float(values[params_size])
				std += math.pow(float(values[params_size + 1]), 2)
				res[key] = [value, std]

				if not is_throughput:
					my_stats = values[params_size + 2:]
					cur_stats = stats.get(key, [])
					if cur_stats == []:
						for i in range(0, len(my_stats)):
							cur_stats.append(0)
					stats[key] = combine_stats(cur_stats, my_stats)

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
		if is_throughput:
			perc = []
		else:
			perc = find_percentages(stats[key])
			perc = list(map(lambda el: str(el), perc))
		data.append(new_key + [str(value), str(std)] + perc)
	data.sort()

	if is_throughput:
		print(max_key, max_value)

	res_file_name = fbase
	if rep:
		res_file_name += '-rep'

	write_to_named_file(res_file_name + '.log', data)

def combine_stats(cur, stats):
	res = []
	for i in range(0, min(len(cur), len(stats))):
		if (i % 2) == 0:
			res.append(stats[i])
		else:
			res.append(cur[i] + int(stats[i]))
	return res

def find_percentages(perc):
	percentages_res = []

	i = 1
	summ = 0
	while i < len(perc):
		summ += perc[i]
		i += 2

	for p in per_values:
		cur_summ = 0
		min_dist = -1
		for i in range(0, len(perc)):
			if (i % 2) == 0:
				value = perc[i]
			else:
				cnt = perc[i]
				cur_summ += cnt
				cur_per = cur_summ * 100.0 / summ
				cur_dist = math.fabs(cur_per - p)
				if (min_dist == -1) or (cur_dist < min_dist): 
					min_dist = cur_dist
					res_value = value
					res_percentage = cur_per
		# percentages_res.append(str(int(res_percentage)))
		percentages_res.append(str(res_value))

	return percentages_res

def most_common(l):
	a = np.array(l)
	counts =  np.bincount(a)
	return np.argmax(counts)

def combine_vms_repetitions(fbase, params_size, is_time=True):
	f = open('./logs_working/' + fbase + '-rep.log', 'r')
	res = {}
	cnts = {}
	for line in f:
		values = line.split(',')
		key = ','.join(values[:params_size])
		[value, std, per] = res.get(key, [0, 0, []])
		cnt = cnts.get(key, 0)
		value += float(values[params_size + 1]) # skipping repetition number
		std += float(values[params_size + 2])
		if is_time:
			if per == []:
				for i in range(0, len(per_values)):
					per.append([])
			for i in range(0, len(per_values)):
				per[i].append(int(values[params_size + 3 + i]))

		res[key] = [value, std, per]
		cnts[key] = cnt + 1


	data = []
	max_value = 0
	for key, values in res.items():
		new_key = key.split(',')
		value = values[0] / cnts[key]
		std = values[1] / cnts[key]
		per = []
		if is_time:
			for i in range(0, len(per_values)):
				per.append(str(most_common(values[2][i])))
		data.append(new_key + [str(value), str(std)] + per)
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
		cnt = len(res[i])
		res[i] = res[i][int(cnt / 5):int(4*cnt / 5)]
		average = np.average(res[i])
		std = np.std(res[i])
		print(str(average) + ' ' + str(std) + ' ' + str(std/average))


# --------- Max throughput task ------------- 

def get_directory(detailed):
	if detailed == 'True':
		directory = 'detailed'
	else:
		directory = 'overall'
	return directory

def get_directory_bool(detailed):
	if detailed:
		directory = 'detailed'
	else:
		directory = 'overall'
	return directory

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

def plot_max_throughput_global_all():
	plot_max_throughput_global(True)
	plot_max_throughput_global(False)

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
	col_num = 0
	for threads in range(0, (max_threads - min_threads) // step_threads + 1):
		plt.errorbar(list(map(lambda el: el + i, x[threads])), y[threads], std[threads], color=colors_6[col_num], fmt='|')
		plt.plot(x[threads], y[threads], label = str(min_threads + threads * step_threads), color=colors_6[col_num])
		i += 3
		col_num += 1
	plt.grid(True)
	if not detailed:
		plt.legend(title = 'Threads', bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
		plt.tight_layout(pad=6)

	plt.title(plot_title_name)
	plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Clients')
	plt.gca().set_ylim(bottom=0)
	plt.gca().set_xlim(left=0)
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
	# fname = 'logs_working/max_throughput-response_time.log'
	x = []
	y = []
	per = []
	std = []

	for threads in range(min_threads, max_threads + 1, step_threads):
		x.append([])
		y.append([])
		std.append([])
		temp = []
		for p in per_values:
			temp.append([])
		per.append(temp)

	with open(fname, 'r') as f:
		for line in f:
			line = line.split(',')
			clients = int(line[0])
			threads_it = (int(line[1]) - min_threads) // step_threads
			x[threads_it].append(clients) 
			y[threads_it].append(float(line[2]))
			std[threads_it].append(float(line[3]))
			i = 0
			for p in per_values:
				per[threads_it][i].append(int(line[4 + i]))
				i += 1

	plot_title_name = 'Maximum throughput experiment'
	plot_file_name = 'plots/max_throughput-response_time_all_%s.png' % dir_name

	t = 0
	for threads in range(0, (max_threads - min_threads) // step_threads + 1):
		plt.plot(x[threads], y[threads], color=colors_6[t], label = str(min_threads + threads * step_threads))
		i = 0
		for p in per_values:
			plt.plot(x[threads], list(map(lambda el: el + t*1000, per[threads][i])), color=colors_6[t])
			i += 1
		t += 1

	plt.grid(True)
	if not detailed:
		plt.legend(title = 'Threads', bbox_to_anchor=(1, 1), loc='upper left', ncol=1)
		plt.tight_layout(pad=6)

	if detailed:
		plt.text(250, 31000, '90%')
		plt.text(250, 6000, '25%')
	else:
		plt.text(450, 75000, '90%')
		plt.text(450, 10000, '25%')

	plt.title(plot_title_name)
	plt.ylabel('Response time [us]')
	plt.xlabel('Clients')
	plt.gca().set_ylim(bottom=0)
	plt.gca().set_xlim(left=0)
	plt.savefig(plot_file_name)
	plt.clf()

def plot_max_throughput_breakdown():
	fname = 'logs_working/detailed-breakdown/max_throughput_210_30.log'
	labels = ['queue', 'servers', 'actively processed']
	values = [2557, 4119, 47]

	plot_title_name = 'Maximum throughput experiment - breakdown of time'
	plot_file_name = 'plots/max_throughput-breakdown.png'

	plt.pie(values, labels=labels,
        autopct='%1.1f%%', startangle=270)
	plt.axis('equal')

	plt.title(plot_title_name, y = 1.04)
	plt.savefig(plot_file_name)
	plt.clf()


# --------- Effect of replication task -------------

servers_values = [3, 5, 7]
replication_factors_values = [1, 2, 3]

replication_experiment_title = '"Effects of replication" experiment'

def plot_replication():
	plot_replication_general('replication', 'replication', is_time=False)
	plot_replication_general('replication-response_time', 'replication-response_time', is_time=True, plot_percentiles=True)
	for type in ['get', 'set', 'all']:
		plot_replication_general('replication-%s' % type, 'replication-%s' % type, header_line=True)
		plot_replication_general('replication-%s' % type, 'replication-%s-queue' % type, 4, True)
		plot_replication_general('replication-%s' % type, 'replication-%s-servers' % type, 6, True)
	for type in ['get', 'set']:
		plot_replication_general('replication-response_time-%s' % type, 'replication-response_time-%s' % type, is_time=True, plot_percentiles=True)
		plot_replication_general('replication-%s' % type, 'replication-%s-scaled' % type, header_line=True, y_lim=25000)

def plot_replication_general(fbase, title, which_params=2, header_line=False, is_time=True, y_lim=-1, plot_percentiles=False):
	print(title)
	fname = 'logs_working/%s.log' % fbase

	x = replication_factors_values
	y = []
	std = []
	per = []
	for servers in servers_values:
		y.append([])
		std.append([])
		temp = []
		for p in per_values:
			temp.append([])
		per.append(temp)

	with open(fname, 'r') as f:
		if header_line:
			next(f)
		for line in f:
			line = line.split(',')
			rep_it = replication_factors_values.index(int(line[0]))
			y[rep_it].append(float(line[which_params])) # assuming somehow sorted
			std[rep_it].append(float(line[which_params + 1])) # assuming somehow sorted
			if is_time and plot_percentiles:
				i = 0
				for p in per_values:
					per[rep_it][i].append(int(line[which_params + 2 + i]))
					i += 1

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
		if is_time and plot_percentiles:
			j = 0
			per_colors = ['w', 'k']
			for p in per_values:
				ax.plot(ind + (i + 0.5) * width, per[i][j], marker='x', markersize=10, mew=2, linestyle='None', color=per_colors[j])
				j += 1
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
	if y_lim != -1:
		plt.gca().set_ylim(top=y_lim)
	plt.title(plot_title_name)
	if is_time:
		plt.ylabel('Time [us]')
	else:
		plt.ylabel('Throughput [ops/s]')
	plt.xlabel('Servers')
	plt.savefig(plot_file_name)
	plt.clf()


# --------- Effect of writes task -------------
writes_percentage_factors = [1, 5, 10]
writes_experiment_title = '"Effects of writes" experiment'

def plot_writes():
	plot_writes_general('writes', 'writes', is_time=False)
	plot_writes_general('writes-response_time', 'writes-response_time', is_time=True)
	for type in ['get', 'set', 'all']:
		plot_writes_general('writes-%s' % type, 'writes-%s' % type, header_line=True)
		plot_writes_general('writes-%s' % type, 'writes-%s-queue' % type, 5, True)
		plot_writes_general('writes-%s' % type, 'writes-%s-servers' % type, 7, True)
	for type in ['get', 'set']:
		plot_writes_general('writes-response_time-%s' % type, 'writes-response_time-%s' % type, is_time=True)

def plot_writes_general(fbase, title, which_params=3, header_line=False, is_time=True):
	print(title)
	fname = 'logs_working/%s.log' % fbase

	for replication in [1, 2]:
		x = writes_percentage_factors
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
				if int(line[2]) == replication:
					y[writes_percentage_factors.index(int(line[0]))].append(float(line[which_params])) # assuming somehow sorted
					std[writes_percentage_factors.index(int(line[0]))].append(float(line[which_params + 1])) # assuming somehow sorted

		N = 3

		ind = np.arange(N)  # the x locations for the groups
		width = 0.25       # the width of the bars

		fig, ax = plt.subplots()
		rects = []
		i = 0
		colors = ['r', 'g', 'b']
		for writes_percentage in writes_percentage_factors:
			rects.append(
					ax.bar(ind + i * width, y[i], width, color=colors[i], yerr=std[i],
							error_kw=dict(ecolor='purple', lw=1, capsize=2, capthick=2)))
			i += 1


		ax.tick_params(axis='x', which='both', top='off', bottom='off')
		ax.set_xticks(ind + 2 * width - 1/8)
		ax.set_xticklabels(('3', '5', '7'))

		legend = ax.legend((rects[0][0], rects[1][0], rects[2][0]), ('1%', '5%', '10%'), title='Percentage of writes',
				bbox_to_anchor=(1, 1), loc='upper left', ncol=1, fontsize='small')
		plt.setp(legend.get_title(),fontsize='x-small')
		plt.tight_layout(pad=9)

		plot_title_name = writes_experiment_title + ', ' + ('R = 1' if replication == 1 else 'R = all')
		plot_file_name = 'plots/' + title + '-' + str(replication) + '-replication.png'

		plt.subplots_adjust(top=0.9, bottom=0.1)
		plt.grid(True)
		plt.gca().set_ylim(bottom=0)
		plt.title(plot_title_name)
		if is_time:
			plt.ylabel('Time [us]')
		else:
			plt.ylabel('Throughput [ops/s]')
		plt.xlabel('Servers')
		plt.savefig(plot_file_name)
		plt.clf()

