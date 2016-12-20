from fabric.api import *
from fabric.context_managers import settings
from fabfiles.common import *
from parse.milestone_3.parse_logs import *

def run_middleware(threads, rep, memcached_string, log_output_file, std_output_file='/dev/null'):
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			runbg('java -jar ./dist/middleware-matusiaa.jar -l 10.0.0.11 -p 11212 \
					-t %d -r %d -m %s' % (threads, rep, memcached_string),
					std_output_file,  log_output_file)

def copy_workloads():
	for host in [2, 3, 4, 9, 10]:
		local('scp asl-fall16-project/workloads/* asl%s:workloads/' % host)

def copy_plots():
	local('cp plots/*.png reports/milestone3/plots')

def copy_fab():
	local('scp -r fabfile* asl11:')
	local('scp -r parse/ asl11:')

def copy_parse(cnt=3):
	hosts = [2, 3, 4, 9, 10]
	for i in range(0, cnt):
		local('scp parse/milestone_3/parse_logs_vms.py asl%s:~' % hosts[i])

def combine_logs(experiment, headers, response_time=False, servers=5, params_size=2, rep=False, directory='logs_working', types=False):
	combine_throughput('%s/%s' % (directory, experiment), headers + ['TPS', 'Standard deviation'], servers, params_size, rep)
	if response_time:
		if types:
			for type in ['get', 'set']:
				combine_response_time('%s/%s-response_time-%s' % (directory, experiment, type),
						headers + ['Response time', 'Standard deviation', '25th percentile', '50th percentile', '90th percentile'],
						servers, params_size, rep)

		combine_response_time('%s/%s-response_time' % (directory, experiment),
				headers + ['Response time', 'Standard deviation', '25th percentile', '50th percentile', '90th percentile'], servers, params_size, rep)


def run_experiments_remote():
	copy_fab()
	# local('scp workloads/* asl11:asl-fall16-project/workloads/')
	with settings(host_string='asl11'):
		runbg('fab run_writes_experiments',
			'fab.log',  '/dev/null')

def run_mm1_experiment():
	hosts = [2, 3, 4]
	run_time = 3 * 60
	stats_time = 1
	pause = 1 * 60
	pause_2 = 15

	clients = 64
	thread_pool = 16

	run_memcached_many(3)

	output = '../logs/mm1_one.log'
	memcached_ips = [12, 14, 4]
	memcached_string = ''
	for ip in memcached_ips:
		memcached_string += '10.0.0.%d:11212 ' % ip
	run_middleware(thread_pool, 3, memcached_string, output)

	time.sleep(pause_2)

	for host in hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients, output, cfg='smallvalue')
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(3)
	time.sleep(pause_2)

def compute_mm1():
	copy_parse()
	for host in [2, 3, 4]:
		with settings(host_string='asl%d' % host):
			run('python3 -c "from parse_logs_vms import *; print(parse_throughput_single(\'logs/mm1.log\'))"')
			run('python3 -c "from parse_logs_vms import *; print(parse_response_time_single(\'logs/mm1.log\'))"')

def run_replication_experiment(servers, replication_factor, repetition): # replication 1, 2, 3 - type
	memaslap_hosts = [2, 3, 4]
	run_time = 3 * 60
	stats_time = 1
	pause = 30
	pause_2 = 15
	clients_per_machine = 70
	threads = 30

	replication_values = [1, round(servers/2), servers]
	replication = replication_values[replication_factor - 1]
	run_memcached_many(servers)

	output = '../logs/improved-replication_%d_%d[%d].log' % (replication_factor, servers, repetition)
	memcached_ips = [12, 14, 4, 13, 5, 10, 8]
	memcached_string = ''
	for i in range(0, servers):
		memcached_string += '10.0.0.%d:11212 ' % memcached_ips[i]
	run_middleware(threads, replication, memcached_string, output)
	time.sleep(pause_2)

	for host in memaslap_hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients_per_machine, output, cfg='replication')
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(servers)
	time.sleep(pause_2)

def run_replication_experiments():
	copy_workloads()

	min_servers = 3
	max_servers = 7
	step_servers = 2

	min_replication = 1
	max_replication = 3

	repetitions = 3
	for servers in range(min_servers, max_servers + 1, step_servers):
		for replication in range(min_replication, max_replication + 1, 1):
			for rep in range(1, repetitions + 1):
				print(str(replication) + ' ' + str(servers) + ' ' + str(rep));
				run_replication_experiment(servers, replication, rep)

def compute_replication_middleware():
	# local('scp parse/milestone_3/parse_logs_vms.py asl11:~')
	local('scp parse/milestone_3/parse_logs_middleware.py asl11:~')
	with settings(host_string='asl11'):
		run('python3 -c "from parse_logs_middleware import *; parse_replication_middleware()"')

def copy_replication_middleware_logs():
	local('scp asl11:logs/improved-replication-*.log ./logs_working/')

def compute_replication():
	copy_parse(3)
	for host in [2, 3, 4]:
		with settings(host_string='asl%d' % host):
			run('python3 -c "from parse_logs_vms import *; parse_replication()"')
	copy_replication_logs()

def combine_replication():
	combine_logs('improved-replication', ['Replication factor', 'Number of servers', 'Repetition'], response_time=False, servers=3, params_size=3, rep=True, types=True)
	combine_max_tps('./logs_working/improved-replication-values', servers=3, params_size=3)
	# combine_logs('improved-replication', ['Replication factor', 'Number of servers', 'Repetition'], response_time=True, servers=3, params_size=3, rep=True, types=True)
	combine_vms_repetitions('improved-replication', ['Replication factor', 'Number of servers'], params_size=2, is_time=False)
	# combine_vms_repetitions('improved-replication-response_time', ['Replication factor', 'Number of servers'], params_size=2)
	# for type in ['get', 'set']:
	# 	combine_vms_repetitions('improved-replication-response_time-%s' % type, ['Replication factor', 'Number of servers'], params_size=2)

def copy_replication_logs():
	hosts = [2, 3, 4]
	for i in range(0, len(hosts)):
		local('scp asl%s:logs/improved-replication.log ./logs_working/improved-replication_%d.log' % (hosts[i], i + 1))
		local('scp asl%s:logs/improved-replication-values.log ./logs_working/improved-replication-values_%d.log' % (hosts[i], i + 1))
		# local('scp asl%s:logs/improved-replication-response_time.log ./logs_working/improved-replication-response_time_%d.log' % (hosts[i], i + 1))
		# for type in ['get', 'set']:
		# 	local('scp asl%s:logs/improved-replication-response_time-%s.log ./logs_working/improved-replication-response_time-%s_%d.log' % (hosts[i], type, type, i + 1))


def run_writes_experiment(servers, percentage, replication_factor, repetition): # replication 1, 2
	memaslap_hosts = [2, 3, 4]
	run_time = 3 * 60
	stats_time = 1
	pause = 30
	pause_2 = 15
	clients_per_machine = 70
	threads = 30

	replication_values = [1, servers]
	replication = replication_values[replication_factor - 1]
	run_memcached_many(servers)

	output = '../logs/improved-writes_%d_%d_%d[%d].log' % (percentage, servers, replication_factor, repetition)
	memcached_ips = [12, 14, 4, 13, 5, 10, 8]
	memcached_string = ''
	for i in range(0, servers):
		memcached_string += '10.0.0.%d:11212 ' % memcached_ips[i]
	run_middleware(threads, replication, memcached_string, output)
	time.sleep(pause_2)

	for host in memaslap_hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients_per_machine, output, ' -w 1k', cfg='writes_' + str(percentage))
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(servers)
	time.sleep(pause_2)

def run_writes_experiments():
	copy_workloads()

	min_servers = 3
	max_servers = 7
	step_servers = 2

	percentages = [1, 5, 10]

	min_replication = 1
	max_replication = 2

	repetitions = 3

	for replication in range(min_replication, max_replication + 1, 1):
		for servers in range(min_servers, max_servers + 1, step_servers):
			for percentage in percentages:
				for repetition in range(1, repetitions + 1):
					print(str(replication) + ' ' + str(servers) + ' ' + str(replication) + ' ' + str(repetition));
					run_writes_experiment(servers, percentage, replication, repetition)



def compute_writes_middleware():
	# local('scp parse/milestone_3/parse_logs_vms.py asl11:~')
	local('scp parse/milestone_3/parse_logs_middleware.py asl11:~')
	with settings(host_string='asl11'):
		run('python3 -c "from parse_logs_middleware import *; parse_writes_middleware()"')

def copy_writes_middleware_logs():
	local('scp asl11:logs/improved-writes-*.log ./logs_working/')

def compute_writes():
	copy_parse(3)
	for host in [2, 3, 4]:
		with settings(host_string='asl%d' % host):
			run('python3 -c "from parse_logs_vms import *; parse_writes()"')
	copy_writes_logs()

def combine_writes():
	combine_logs('improved-writes', ['Replication factor', 'Number of servers', 'Repetition'], response_time=False, servers=3, params_size=4, rep=True, types=True)
	combine_max_tps('./logs_working/improved-writes-values', servers=3, params_size=4)
	# combine_logs('improved-writes', ['Replication factor', 'Number of servers', 'Repetition'], response_time=True, servers=3, params_size=3, rep=True, types=True)
	combine_vms_repetitions('improved-writes', ['Replication factor', 'Number of servers'], params_size=3, is_time=False)
	# combine_vms_repetitions('improved-writes-response_time', ['Replication factor', 'Number of servers'], params_size=2)
	# for type in ['get', 'set']:
	# 	combine_vms_repetitions('improved-writes-response_time-%s' % type, ['Replication factor', 'Number of servers'], params_size=2)

def copy_writes_logs():
	hosts = [2, 3, 4]
	for i in range(0, len(hosts)):
		local('scp asl%s:logs/improved-writes.log ./logs_working/improved-writes_%d.log' % (hosts[i], i + 1))
		local('scp asl%s:logs/improved-writes-values.log ./logs_working/improved-writes-values_%d.log' % (hosts[i], i + 1))
		# local('scp asl%s:logs/improved-writes-response_time.log ./logs_working/improved-writes-response_time_%d.log' % (hosts[i], i + 1))
		# for type in ['get', 'set']:
		# 	local('scp asl%s:logs/improved-writes-response_time-%s.log ./logs_working/improved-writes-response_time-%s_%d.log' % (hosts[i], type, type, i + 1))

