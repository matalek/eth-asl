
from fabric.api import *
from fabric.context_managers import settings
import time

env.use_ssh_config = True

def deploy():
	local('git push')
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			run('git pull')
			run('ant')

def clear_keys():
	for host_number in [1, 2, 3, 4, 5, 6, 11]:
		local('ssh-keygen \
			-R matusiaaforaslvms%d.westeurope.cloudapp.azure.com' % host_number)

def copy_parse():
	for host in ['asl2', 'asl3', 'asl4']:
		local('scp parse_logs_vms.py %s:~' % host)

def import_baseline_logs():
	for host in ['asl2', 'asl3']:
		local('scp %s:~/logs/throughput* ./logs/' % host)
		local('scp %s:~/logs/response_time* ./logs/' % host)

def import_stability_logs():
	for host in ['asl2', 'asl3', 'asl4']:
		local('scp %s:~/logs/stability_parsed* ./logs/' % host)

def run_middleware(threads, rep):
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			runbg('java -jar ./dist/middleware-matusiaa.jar -l 10.0.0.11 -p 11212 \
				-t %d -r %d -m 10.0.0.12:11212 10.0.0.14:11212 10.0.0.4:11212' % (threads, rep),
				'../logs/servers_distribution.log')

def run_memcached(host='asl1'):
	with settings(host_string=host):
		runbg('memcached -p 11212 -t 1')

def run_memaslap_async(host, sut, run_time, stats_time, clients, output):
	with settings(host_string=host):
		with cd('libmemcached-1.0.18'):
			runbg('./clients/memaslap -s %s:11212 -T %d -c %d -o 0.9 -S %ss -t %ss -F ../workloads/smallvalue.cfg' 
					% (sut, clients, clients, stats_time, run_time),
					output)

def stop_middleware():
	with settings(host_string='asl11'):
		run('pkill -f middleware')

def stop_memcached(host):
	with settings(host_string=host):
		run('sudo pkill -f memcached')

def stop_all_memcached():
	for host in ['asl1', 'asl5', 'asl6']:
		stop_memcached(host)

def stop_all():
	stop_middleware()
	stop_all_memcached()

def runbg(cmd, output_file=None, sockname="dtach"):
	if output_file:
		cmd = "/bin/bash -c '{} > {}'".format(cmd, output_file)
	else:
		cmd = "/bin/bash -c '{} > /dev/null 2> /dev/null'".format(cmd)
	return run('dtach -n `mktemp -u /tmp/%s.XXXX` %s'  % (sockname,cmd))

def run_experiments():
	run_time = '30s'
	max_clients = 32
	run_memcached()
	for clients in range(1, max_clients + 1):
		run_memaslap(run_time, clients)
	stop_memcached()

def run_baseline_experiments(series_number = '1'):
	run_time = 30
	pause = 5
	max_clients = 64
	memcached_server = '10.0.0.12'
	output = '../logs/microbench%d_%s.log' % (clients, series_number)
	run_memcached()
	for clients in range(1, max_clients + 1):
		run_memaslap_async('asl2', memcached_server, run_time, run_time, clients, output)
		run_memaslap_async('asl3', memcached_server, run_time, run_time, clients, output)
		time.sleep(run_time + pause)
	stop_memcached()

def run_stability_experiment():
	run_time = 60 * 60
	stats_time = 10
	pause = 10
	threads = 16
	rep = 3
	middleware_server = '10.0.0.11'
	run_memcached('asl1')
	run_memcached('asl5')
	run_memcached('asl6')
	run_middleware(threads, rep)
	run_memaslap_async('asl2', middleware_server, run_time, stats_time, 64, '../logs/stability.log')
	run_memaslap_async('asl3', middleware_server, run_time, stats_time, 64, '../logs/stability.log')
	run_memaslap_async('asl4', middleware_server, run_time, stats_time, 64, '../logs/stability.log')
	time.sleep(run_time + pause)
	stop_middleware()
	stop_memcached('asl1')
	stop_memcached('asl5')
	stop_memcached('asl6')

def compute_baseline():
	copy_parse()
	clients = 64
	hosts = [['asl2', 1], ['asl3', 2]]
	for host in hosts:
		with settings(host_string=host[0]):
			run('python3 -c "from parse_logs_vms import *; parse_baseline(%d, \'%d\')"' % (clients, host[1]))
	import_baseline_logs()
	local('python3 -c "from parse_logs import *; combine_baseline()"')
	local('python3 -c "from parse_logs import *; draw_baseline_plots()"')

def compute_stability():
	copy_parse()
	hosts = [['asl2', 1], ['asl3', 2], ['asl4',3]]
	for host in hosts:
		with settings(host_string=host[0]):
			run('python3 -c "from parse_logs_vms import *; parse_stability(%d)"' % host[1])
	import_stability_logs()
	local('python3 -c "from parse_logs import *; combine_stability()"')
	local('python3 -c "from parse_logs import *; draw_stability_plots()"')

def copy_compressed_logs():
	for host in ['asl2', 'asl3', 'asl4']:
		local('scp %s:~/logs*.tar.gz ./logs/' % host)

