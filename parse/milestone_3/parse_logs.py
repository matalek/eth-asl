from parse.common import *

def count_service_time(fname):
	with open(fname, 'r') as f:
		next(f)
		for line in f:
			line = line.split(',')
			move = 5
			start = 2
			servers = int(line[1])
			total = float(line[start])
			queue = float(line[start + move])
			server = float(line[start + 2 * move])
			accept = float(line[start + 3 * move])
			jobs = float(line[start + 4 * move])
			print(line[0] + ' ' + line[1])
			print(str(accept))
			 # + ' ' + str(server/jobs/servers))

def count_max_tps(fname):

	with open(fname, 'r') as f:
		lines = f.readlines()
		n = len(lines[0].split(','))
		tps = []
		for i in range(0, n):
			tps.append(0)
		for line in lines:
			line = line.split(',')
			for i in range(0, n):
				tps[i] += int(line[i])

		print(np.max(tps))

def combine_max_tps(fbase, servers, params_size):
	files = []
	for i in range(1, servers + 1):
		files.append(open(fbase + '_' + str(i) + '.log', 'r').readlines())

	conf_cnt = len(files[0])
	n = len(files[0][0].split(',')) - params_size

	res = []
	mx = {}
	for i in range(0, conf_cnt):
		tps = []
		for j in range(0, n):
			tps.append(0)
		for j in range(0, servers):
			line = files[j][i].split(',')
			for k in range(0, n):
				tps[k] += int(line[k + params_size])
		key = ''
		for j in range(0, params_size - 1):
			key += line[j] + ','
		key = key[:-1]
		tmp = mx.get(key, 0)
		tmp = max(tmp, np.max(tps))
		mx[key] = tmp

	for key in mx:
		res.append(key.split(',') + [str(mx[key])])

	res.sort()

	write_to_named_file(fbase + '.log', res)


def calculate_util_max(fbase, params_size):
	f = open(fbase + '.log', 'r').readlines()
	f = f[1:]
	v = open(fbase + '-values.log', 'r').readlines()

	conf_cnt = len(v)

	res = []
	for i in range(0, conf_cnt):
		lf = f[i].split(',')
		lv = v[i].split(',')
		tps = float(lf[params_size])

		servers = int(lf[1])
		rep_factor = int(lf[0])
		if rep_factor == 1:
			rep = 1
		if rep_factor == 2:
			rep = math.ceil(servers / 2)
		if rep_factor == 3:
			rep = servers

		w = 0.05
		# tps *= (1 + w * (rep - 1))

		print((1 + w * (rep - 1)))

		mu = float(lv[params_size])
		util = tps/mu
		# util *= (1 + w * (rep - 1))
		print(util)


		res.append(lf[:params_size] + [str(util)])

	write_to_named_file(fbase + '-util.log', res)


def calculate_util(fbase, conf_cnt):
	ft = open(fbase + '.log', 'r')
	lsft = ft.readlines()
	fm = open(fbase + '-all.log', 'r')
	lsfm = fm.readlines()

	fmg = open(fbase + '-get.log', 'r')
	lsfmg = fmg.readlines()
	fms = open(fbase + '-set.log', 'r')
	lsfms = fms.readlines()


	for i in range(1, conf_cnt + 1):
		start = 2
		move = 5

		lft = lsft[i].split(',')
		lfm = lsfm[i].split(',')
		lfmg = lsfmg[i].split(',')
		lfms = lsfms[i].split(',')

		server = float(lfm[start + 2 * move])
		jobs = float(lfmg[start + 4 * move]) + float(lfms[start + 4 * move])
		# print(float(lfmg[start + 4 * move]))
		# print(float(lfms[start + 4 * move]))
		tps = float(lft[2])
		# print(jobs)
		mu = 10**6 * jobs / server
		util = tps / mu
		# print(server)
		# print(mu)
		# print(tps)
		# print(mu)
		# print(jobs)
		print(util)