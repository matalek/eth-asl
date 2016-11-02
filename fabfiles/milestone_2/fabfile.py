from fabric.api import *
from fabric.context_managers import settings
from fabfiles.common import *
from parse.milestone_2.parse_logs import *

def copy_parse():
	for host in [2, 3, 4, 9, 10]:
		local('scp parse/milestone_2/parse_logs_vms.py asl%s:~' % host)

def copy_workloads():
	for host in [2, 3, 4, 9, 10]:
		local('scp workloads/* asl%s:workloads/' % host)

def run_memcached_many(cnt=5):
	hosts = [1, 5, 6, 7, 8]
	for i in range(0, cnt):
		run_memcached('asl' + str(hosts[i]), ' -m 256')

def stop_memcached_many(cnt=5):
	servers = [1, 5, 6, 7, 8, 9, 10]
	for i in range(0, cnt):
		stop_memcached('asl' + str(servers[i]))

def stop_memaslap_many(cnt=5):
	servers = [2, 3, 4, 9, 10]
	for i in range(0, cnt):
		stop_memaslap('asl' + str(servers[i]))

def run_middleware(threads, rep, memcached_string, log_output_file):
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			runbg('java -jar ./dist/middleware-matusiaa.jar -l 10.0.0.11 -p 11212 \
					-t %d -r %d -m %s' % (threads, rep, memcached_string),
					'/dev/null',  log_output_file)

def run_max_throughput_experiment(clients, thread_pool):
	hosts = [2, 3, 4, 9, 10]
	run_time = 5 * 60
	stats_time = 30
	pause = 3 * 60

	run_memcached_many(5)

	output = '../logs/max_throughput_%d_%d.log' % (clients * len(hosts), thread_pool)
	memcached_ips = [12, 14, 4, 13, 5]
	memcached_string = ''
	for ip in memcached_ips:
		memcached_string += '10.0.0.%d:11212 ' % ip 
	run_middleware(thread_pool, 1, memcached_string, output)

	for host in hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients, output, ' -w 1k', 'max_throughput')
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(5)

def run_max_throughput_experiments():
	copy_workloads()

	min_clients_per_machine = 90
	max_clients_per_machine = 150
	clients_step = 2

	min_thread_pool = 8
	max_thread_pool = 16
	thread_pool_step = 8

	for clients in range(min_clients_per_machine, max_clients_per_machine + 1, clients_step):
		for thread_pool in range(min_thread_pool, max_thread_pool + 1, thread_pool_step):
			run_max_throughput_experiment(clients, thread_pool)

def compute_max_throughput():
	copy_parse()
	for host in [2, 3, 4, 9, 10]:
		with settings(host_string='asl%d' % host):
			run('python3 -c "from parse_logs_vms import *; parse_max_throughput()"')
	copy_max_throughput_logs()

def combine_max_throughput():
	combine_throughput('logs_working/max_throughput')
	combine_response_time('logs_working/max_throughput-response_time')

def copy_max_throughput_logs():
	hosts = [2, 3, 4, 9, 10]
	for i in range(0, len(hosts)):
		local('scp asl%s:logs/max_throughput.log ./logs_working/max_throughput_%d.log' % (hosts[i], i + 1))
		local('scp asl%s:logs/max_throughput-response_time.log ./logs_working/max_throughput-response_time_%d.log' % (hosts[i], i + 1))

def run_replication_experiment(servers, replication_factor): # replication 1, 2, 3 - type
	memaslap_hosts = [2, 3, 4]
	run_time = 5 * 60 # TODO: change
	stats_time = 30
	pause = 3 * 60 # TODO: change
	clients_per_machine = 100 # TODO: put another value
	threads = 10 # TODO: put another value

	replication_values = [1, round(servers/2), servers]
	replication = replication_values[replication_factor]
	run_memcached_many(servers)

	output = '../logs/replication_%d_%d.log' % (replication_factor, servers)
	memcached_ips = [12, 14, 4, 13, 5, 10, 8]
	memcached_string = ''
	for i in range(0, servers):
		memcached_string += '10.0.0.%d:11212 ' % memcached_ips[i] 
	run_middleware(thread_pool, replication, memcached_string, output)

	for host in memaslap_hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients_per_machine, output, ' -w 1k', 'replication')
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(servers)

def run_replication_experiments():
	copy_workloads()

	min_servers = 3
	max_servers = 7
	step_servers = 2

	min_replication = 1
	max_replication = 3

	for servers in range(min_servers, max_servers + 1, step_servers):
		for replication in range(min_replication, max_replication + 1, 1):
			run_replication_experiment(servers, replication)

def run_writes_experiment(servers, percentage, replication_factor): # replication 1, 2
	memaslap_hosts = [2, 3, 4]
	run_time = 5 * 60 # TODO: change
	stats_time = 30
	pause = 3 * 60 # TODO: change
	clients_per_machine = 100 # TODO: put another value
	threads = 10 # TODO: put another value

	replication_values = [1, servers]
	replication = replication_values[replication_factor]
	run_memcached_many(servers)

	output = '../logs/writes_%d_%d.log' % (replication_factor, servers)
	memcached_ips = [12, 14, 4, 13, 5, 10, 8]
	memcached_string = ''
	for i in range(0, servers):
		memcached_string += '10.0.0.%d:11212 ' % memcached_ips[i] 
	run_middleware(thread_pool, replication, memcached_string, output)

	for host in memaslap_hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients_per_machine, output, ' -w 1k', 'writes_' + str(percentage))
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(servers)

def run_writes_experiments():
	copy_workloads()

	min_servers = 3
	max_servers = 7
	step_servers = 2

	percentages = [1, 5, 10]

	min_replication = 1
	max_replication = 2

	for servers in range(min_servers, max_servers + 1, step_servers):
		for percentage in percentages:
			for replication in range(min_replication, max_replication + 1, 1):
				run_writes_experiment(servers, percentage, replication)
