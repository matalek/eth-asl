import numpy as np

stats_cnt = 3
times_cnt = 6

# per_values = [25, 50, 90]
per_values = [90]

service_time = 2591
time_measured = 30

def parse_middleware_times_single(fname, type):
	print(fname)
	res = []
	times = []
	for i in range(0, stats_cnt + 1):
		res.append([])
	for i in range(0, times_cnt):
		times.append([])

	numbers = []
	with open(fname, 'r') as f:
		lines = f.readlines()
		j = 1
		while j < len(lines):
			line = lines[j].split()
			if (line[1] == type) or (type == 'all'):
				for i in range(0, stats_cnt):
					res[i].append(int(line[2 + i]))
				# res[stats_cnt].append(int(line[2 + stats_cnt + 1 + 5]) - int(line[2 + stats_cnt + 1 + 2]))
				# for i in range(0, times_cnt):
				# 	times[i].append(int(line[2 + stats_cnt + 1 + i]))
				# print(int(line[2 + stats_cnt + 1]))
				numbers.append(int(line[2 + stats_cnt + 1]))
			j += 2


	data = []
	for i in range(0, stats_cnt):
		cnt = len(res[i])
		res[i] = res[i][int(cnt / time_measured):int((time_measured - 1) * cnt / time_measured)]
		data += [str(np.average(res[i])), str(np.std(res[i]))]
		for p in per_values:
			data.append(str(np.percentile(res[i], p)))

	# number = 0
	# for i in range(0, times_cnt):
	# 	times[i] = times[i][int(cnt / 5):int(4 * cnt / 5)]

	cnt = len(numbers)
	numbers = numbers[int(cnt / time_measured):int((time_measured - 1)  * cnt / time_measured)]

	# i = 0
	# start_time = times[3][i]
	# start_i = i
	# numbers = []
	# while i < len(times[3]):

	# 	if times[3][i] > start_time + service_time:
	# 		numbers.append((i - start_i) * 5)
	# 		start_time = times[3][i]
	# 		start_i = i
	# 	i += 1
	print(np.average(numbers))
	print(np.std(numbers))

	return data