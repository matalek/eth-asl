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

	fmg = open(fbase + '-get.log', 'r')
	lsfmg = fmg.readlines()
	fms = open(fbase + '-set.log', 'r')
	lsfms = fms.readlines()

	conf_cnt = len(v)

	res = []
	for i in range(0, conf_cnt):
		lf = f[i].split(',')
		lv = v[i].split(',')
		tps = float(lf[params_size])


		start = 2
		move = 5
		lfmg = lsfmg[i + 1].split(',')
		lfms = lsfms[i + 1].split(',')
		jobs_get = float(lfmg[start + 4 * move + 1])
		jobs_set = float(lfms[start + 4 * move + 1])
		jobs = float(lfmg[start + 4 * move]) + float(lfms[start + 4 * move])

		print(jobs)

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


		res.append(lf[:params_size] + [str(tps), str(mu), str(jobs_get), str(jobs_set)])

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

def rep_cal(rep_factor, servers, is_replication):
	if rep_factor == 1:
		return 1
	if not is_replication: # rep_factor = 2 (all)
		return servers
	if rep_factor == 2:
		return math.ceil(servers / 2)
	if rep_factor == 3:
		return servers

def str_rep(rep_factor, is_replication):
	if rep_factor == 1:
		return 'none'
	if not is_replication: # rep_factor = 2 (all)
		return 'all'
	if rep_factor == 2:
		return 'half'
	if rep_factor == 3:
		return 'all'

def calculate_stats(fbase, is_replication=False):

	if is_replication:
		w = 0.05
		params_size = 2
	else:
		params_size = 3
	f = open(fbase + '-util.log', 'r')

	f_times = open(fbase + '-all.log', 'r')
	next(f_times)

	total_stats = []

	f_l = f.readlines()
	f_times_l = f_times.readlines()

	for i in range(0, len(f_l)):
		line = f_l[i]
		line_times = f_times_l[i].split(',')

		line = line.split(',')
		m = int(line[1])

		if is_replication:
			rep_factor = int(line[0])
		else:
			rep_factor = int(line[2])
			w = float(line[0]) / 100

		if (m == 5) or (str_rep(rep_factor, is_replication) == 'half') or (w == 0.05):
			continue

		rep = rep_cal(rep_factor, m, is_replication)
		tps = float(line[params_size])
		ser = float(line[params_size + 1])
		# mul = (1 + w * (rep - 1))
		mul = 1
		lam = tps * mul
		mu = ser / m * mul
		rho = tps/ser

		requests_get = float(line[params_size + 2])
		requests_set = float(line[params_size + 3])
		requests = requests_set + requests_get

		p_base = float((m * rho)**m) / (math.factorial(m) * (1 - rho))
		p_0 = 1 + p_base
		for n in range (1, m):
			p_0 += (m * rho)**n / math.factorial(n)
		p_0 = 1 / p_0
		p_q = p_base * p_0

		en = m * rho + rho / (1 - rho) * p_q
		enq = rho / (1 - rho) * p_q
		ens = en - enq

		er = 1 / mu * (1 + p_q / (m * (1-rho))) * 10**6
		ew = enq / lam * 10**6
		# ew2 = p_q / (m * mu * (1-rho))
		es = 1/mu * 10**6

		# Middleware times
		start = 3
		move = 5
		t_r = float(line_times[start])
		t_w = float(line_times[start + move])
		t_s = float(line_times[start + 2* move])


		# Adding stats

		inits = [m, str_rep(rep_factor, is_replication)]
		if not is_replication:
			inits.append("%.0f" % (w * 100))


		stats = inits
		# stats += ["%.0f" % tps, "%.0f" % lam, "%.0f" % ser, "%.0f" % mu]
		# stats += ["%.3f" % rho, "%.3f" % p_0, "%.3f" % p_q, "%.2f" % en, "%.2f" % enq, "%.2f" % ens,  "%.2f" % requests_get, "%.2f" % requests_set, "%.2f" % requests, "%.2f" % (requests/ens)]
		stats += [ "%.0f" % er, "%.0f" % ew, "%.0f" % es, "%.0f" % t_r, "%.0f" % t_w, "%.0f" % t_s, "%.2f" % (t_w/ew), "%.2f" % (t_s/es), "%.2f" % (requests/m), "%.2f" % (es/ew), "%.2f" % (t_s/t_w)]
		total_stats.append(stats)



	if is_replication:
		sort_key = lambda x : x[0]
	else:
		sort_key = lambda x : str(x[2]) + '#' + str(x[1] + 'z')[3] + '#' + to_str(x[0])
	total_stats.sort(key = sort_key)

	for s in total_stats:
		print_stats(s)

def to_str(x):
	if int(x) < 10:
		return '0' + str(x)
	return str(x)

def print_stats(stats):
	res = '\hline '
	i = 0
	for s in stats:
		res += str(s)
		if i != len(stats) - 1:
			res += ' & '
		i += 1
	res += ' \\\\ '
	print(res)
