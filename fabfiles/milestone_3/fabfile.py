from fabric.api import *
from fabric.context_managers import settings
from fabfiles.common import *

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
	# local('scp -r parse/ asl11:')

def copy_parse(cnt=3):
	hosts = [2, 3, 4, 9, 10]
	for i in range(0, cnt):
		local('scp parse/milestone_3/parse_logs_vms.py asl%s:~' % hosts[i])

def run_experiments_remote():
	copy_fab()
	# local('scp workloads/* asl11:asl-fall16-project/workloads/')
	with settings(host_string='asl11'):
		runbg('fab run_mm1_experiment',
			'fab.log',  '/dev/null')

def run_mm1_experiment():
	hosts = [2, 3, 4]
	run_time = 30 * 60
	stats_time = 1
	pause = 1 * 60
	pause_2 = 15

	clients = 64
	thread_pool = 16

	run_memcached_many(3)

	output = '../logs/mm1.log'
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
