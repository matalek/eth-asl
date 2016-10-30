from fabric.api import *
from fabric.context_managers import settings
from fabfiles.common import *
from parse.milestone_2.parse_logs import combine_max_throughput

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
	servers = [1, 5, 6, 7, 8]
	for i in range(0, cnt):
		stop_memcached('asl' + str(servers[i]))

def run_middleware(threads, rep, memcached_string, log_output_file):
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			runbg('java -jar ./dist/middleware-matusiaa.jar -l 10.0.0.11 -p 11212 \
					-t %d -r %d -m %s' % (threads, rep, memcached_string),
					'/dev/null',  log_output_file)

def run_max_throughput_experiment(clients, thread_pool):
	hosts = [2, 3, 4, 9, 10]
	run_time = 2 * 60
	stats_time = 30
	pause = 10

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

	min_clients_per_machine = 40
	max_clients_per_machine = 100
	clients_step = 10

	min_thread_pool = 10
	max_thread_pool = 20
	thread_pool_step = 10

	for clients in range(min_clients_per_machine, max_clients_per_machine + 1, clients_step):
		for thread_pool in range(min_thread_pool, max_thread_pool + 1, thread_pool_step):
			run_max_throughput_experiment(clients, thread_pool)

def compute_max_throughput():
	copy_parse()
	for host in [2, 3, 4, 9, 10]:
		with settings(host_string='asl%d' % host):
			run('python3 -c "from parse_logs_vms import *; parse_max_throughput()"')
	copy_max_throughput_logs()

def copy_max_throughput_logs():
	hosts = [2, 3, 4, 9, 10]
	for i in range(0, len(hosts)):
		local('scp asl%s:logs/max_throughput.log ./logs_working/max_throughput_%d.log' % (hosts[i], i + 1))
