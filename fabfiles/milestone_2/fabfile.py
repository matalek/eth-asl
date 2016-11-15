from fabric.api import *
from fabric.context_managers import settings
from fabfiles.common import *
from parse.milestone_2.parse_logs import *

def start_vms():
	for host in range(1, 12):
		local('azure vm start FOR_ASL foraslvms%d &' % host)

def stop_vms():
	for host in range(1, 12):
		local('azure vm deallocate FOR_ASL foraslvms%d &' % host)

def copy_key():
	for host in range(1, 11):
		with settings(host_string='asl%d' % host):
			run("echo \"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCioUBurO+ZmvEMYKddsWVXn+n9M2VkUFTk0otxsHYhrWtQpHLfeJzBOFuzg7QmEYGABwyH5BmwxoiRxhmfGMUPjDcghb++iyYlR5QmP59yehV1glUWlSGajiKHOE8CGU4xf5pgZKfIJroL5XqVe0V+eIYeGMleqS3l982eC6C+CQAWb1Jg55JRYcR8zKbIkyejAkJXun1DXk1zjt9qsGtXgLpHFuTGL9/37FAixUsuAI0oJNiiGYYlrsZxEDVtj8FpGGNfR9DgZElrCdkkhUJyRPVL4K1U3J6B1NvMhV/O18ptaUIVo970dw4QBV82GfU2oN3mJybbc3h5vMxHmIkYnkZ1bR/B2JvbBAHbcY0nSG/JpxaNjcePIfpkVj2Q4+vwJyPGfCHYZsWCXoLkC8gpmk+cAVQDQtBl7/D2P/lV+7TnWBCblbQpohwSPbmnS8cFZe0qX4QVX/mIPzPUu/prKi4DbPcNFQXn1sEdWr5e0LyQkKG5oKC5tFOqCwxJmVtA80YfN+JLficLpBf7srUH3DkAdPbf2ohNnnuNa+5zexOj0RW7zevhVXpT/SUvbNwyt0JZJhdpUemuxd1jCBKBZ9mvGrFFUfEAD2ymfPYFzmLegQAoa7knOToCN8+joWeNJ81c0aZqBec2o2ZxrcUgMAi/WIRkvrurj+9UFapFpw== matusiaa@foraslvms11\" >> .ssh/authorized_keys")

def copy_fab():
	local('scp -r fabfile* asl11:')
	local('scp -r parse/ asl11:')

def copy_parse(cnt=5):
	hosts = [2, 3, 4, 9, 10]
	for i in range(0, cnt):
		local('scp parse/milestone_2/parse_logs_vms.py asl%s:~' % hosts[i])

def copy_workloads():
	for host in [2, 3, 4, 9, 10]:
		local('scp asl-fall16-project/workloads/* asl%s:workloads/' % host)

def copy_plots():
	local('cp plots/*.png reports/milestone2/plots')

def run_memcached_many(cnt=5):
	hosts = [1, 5, 6, 7, 8, 9, 10]
	for i in range(0, cnt):
		run_memcached('asl' + str(hosts[i]), ' -m 256')

def stop_memcached_many(cnt=7):
	servers = [1, 5, 6, 7, 8, 9, 10]
	for i in range(0, cnt):
		stop_memcached('asl' + str(servers[i]))

def stop_memaslap_many(cnt=5):
	servers = [2, 3, 4, 9, 10]
	for i in range(0, cnt):
		stop_memaslap('asl' + str(servers[i]))

def run_middleware(threads, rep, memcached_string, log_output_file, std_output_file='/dev/null'):
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			runbg('java -jar ./dist/middleware-matusiaa.jar -l 10.0.0.11 -p 11212 \
					-t %d -r %d -m %s' % (threads, rep, memcached_string),
					std_output_file,  log_output_file)

def combine_logs(experiment, response_time=False, servers=5, repetitions=False):
	combine_throughput('logs_working/%s' % experiment, servers, repetitions)
	if response_time:
		combine_response_time('logs_working/%s-response_time' % experiment, servers, repetitions)

def run_experiments_remote():
	copy_fab()
	local('scp workloads/* asl11:asl-fall16-project/workloads/')
	with settings(host_string='asl11'):
		runbg('fab run_writes_experiments',
			'fab.log',  '/dev/null')

# --------- Max throughput task ------------- 

def run_max_throughput_experiment(clients, thread_pool):
	hosts = [2, 3, 4, 9, 10]
	run_time = 5 * 60
	stats_time = 1
	pause = 2 * 60
	pause_2 = 15

	run_memcached_many(5)

	output = '../logs/max_throughput_%d_%d.log' % (clients * len(hosts), thread_pool)
	std_output = '../logs/std_max_throughput_%d_%d.log' % (clients * len(hosts), thread_pool)
	log_output = '../logs/log_max_throughput_%d_%d.log' % (clients * len(hosts), thread_pool)
	memcached_ips = [12, 14, 4, 13, 5]
	memcached_string = ''
	for ip in memcached_ips:
		memcached_string += '10.0.0.%d:11212 ' % ip 
	run_middleware(thread_pool, 1, memcached_string, output, std_output)

	time.sleep(pause_2)

	for host in hosts:
		run_memaslap_async('asl' + str(host), run_time, stats_time, clients, output, ' -w 1k', 'max_throughput', log_output)
	time.sleep(run_time + pause)

	stop_middleware()
	stop_memcached_many(5)
	time.sleep(pause_2)

def run_max_throughput_experiments():
	copy_workloads()

	min_clients_per_machine = 20
	max_clients_per_machine = 100
	clients_step = 10

	min_thread_pool = 10
	max_thread_pool = 60
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

def combine_max_throughput():
	combine_logs('max_throughput', True)

def copy_max_throughput_logs():
	hosts = [2, 3, 4, 9, 10]
	for i in range(0, len(hosts)):
		local('scp asl%s:logs/max_throughput.log ./logs_working/max_throughput_%d.log' % (hosts[i], i + 1))
		local('scp asl%s:logs/max_throughput-response_time.log ./logs_working/max_throughput-response_time_%d.log' % (hosts[i], i + 1))

def copy_max_throughput_compressed():
	i = 1
	for host in [2, 3, 4, 9, 10]:
		# local('scp asl%s:logs/overall.tar.gz logs/milestone2/overall%d.tar.gz' % (host, i))
		local('scp asl%s:logs/detailed.tar.gz logs/milestone2/detailed_%d.tar.gz' % (host, i))
		i += 1


# --------- Effect of replication task -------------

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

	output = '../logs/replication_%d_%d[%d].log' % (replication_factor, servers, repetition)
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
	# copy_workloads()

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

def compute_replication():
	copy_parse(3)
	for host in [2, 3, 4]:
		with settings(host_string='asl%d' % host):
			run('python3 -c "from parse_logs_vms import *; parse_replication()"')
	copy_replication_logs()

def compute_replication_middleware():
	local('scp parse/milestone_2/parse_logs_vms.py asl11:~')
	local('scp parse/milestone_2/parse_logs_middleware.py asl11:~')
	with settings(host_string='asl11'):
		run('python3 -c "from parse_logs_middleware import *; parse_replication_middleware()"')

def combine_replication():
	combine_logs('replication', servers=3, repetitions=True)
	combine_vms_repetitions('replication')

def copy_replication_logs():
	hosts = [2, 3, 4]
	for i in range(0, len(hosts)):
		local('scp asl%s:logs/replication.log ./logs_working/replication_%d.log' % (hosts[i], i + 1))
		# local('scp asl%s:logs/max_throughput-response_time.log ./logs_working/max_throughput-response_time_%d.log' % (hosts[i], i + 1))

def copy_replication_middleware_logs():
	local('scp asl11:logs/replication-*.log ./logs_working/')

# --------- Effect of writes task -------------

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

	output = '../logs/writes_%d_%d_%d[%d].log' % (percentage, servers, replication_factor, repetition)
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

	for servers in range(min_servers, max_servers + 1, step_servers):
		for percentage in percentages:
			for replication in range(min_replication, max_replication + 1, 1):
				for repetition in range(1, repetitions + 1):
					print(str(replication) + ' ' + str(servers) + ' ' + str(replication) + ' ' + str(repetition));
					run_writes_experiment(servers, percentage, replication, repetition)


def combine_writes():
	combine_logs('writes')

#-------------------------------------------

def move_logs():
	copy_parse(3)
	directory_name = 'replication_old'
	for host in [2, 3, 4]:
		with settings(host_string='asl%d' % host):
			run('mkdir -p logs/%s' % directory_name)
			run('python3 -c "from parse_logs_vms import *; move_logs(\'%s\')"' % directory_name)
			with cd('logs'):
				run('tar -zcvf %s.tar.gz %s' % (directory_name, directory_name))
