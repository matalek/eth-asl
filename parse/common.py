import numpy as np
import math

def write_to_file(name, content):
	fres = 'logs/' + name + '.log'
	write_to_named_file(fres, content)

def write_to_named_file(fname, content):
	with open(fname, 'w+') as f:
		for val in content:
			i = 0
			for el in val:
				f.write(el)
				i += 1
				if i != len(val):
					f.write(',')
			f.write('\n')

# --------- Combining -------------

per_values = [25, 90]

def combine_throughput(fbase, headers=[], servers=5, params_size=2, rep=False):
	combine(fbase, headers, True, servers, params_size, rep)

def combine_response_time(fbase, headers=[], servers=5, params_size=2, rep=False):
	combine(fbase, headers, False, servers, params_size, rep)

def combine(fbase, headers, is_throughput, servers, params_size=2, rep=False):
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

	data = [headers] + data
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

def combine_vms_repetitions(fbase, headers, params_size, is_time=True):
	print(fbase)
	f = open('./logs_working/' + fbase + '-rep.log', 'r')
	res = {}
	cnts = {}
	lines = f.readlines()[1:]
	for line in lines:
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

	avgs = []
	stds = []
	for line in lines:
		values = line.split(',')
		key = ','.join(values[:params_size])
		[value, std, per] = res.get(key, [0, 0, []])
		avg = value / cnts[key]
		std = std / cnts[key]
		avgs.append(abs(avg - float(values[params_size + 1])) / avg)
		stds.append(abs(std - float(values[params_size + 2])) / std)
	print(np.average(avgs))
	print(np.average(stds))

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

	if is_time:
		headers = headers + ['Response time', 'Standard deviation', '25th percentile', '50th percentile', '90th percentile']
	else:
		headers = headers + ['TPS', 'Standard deviation']

	data = [headers] + data
	write_to_named_file('./logs_working/' + fbase + '.log', data)
