
from fabric.api import *
from fabric.context_managers import settings
import time

env.use_ssh_config = True

def deploy():
	local('git push')
	with settings(host_string='asl11'):
		run('cd asl-fall16-project')
		run('git pull')

def copy_parse():
	for host in ['asl2', 'asl3']:
		local('scp parse_logs.py %s:~' % host)	

def run_middleware():
	threads = 3
	rep = 1
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			runbg('java -jar ./dist/middleware-matusiaa.jar -I 10.0.0.4 -p 11212 -t %d -r %d -m 10.0.0.5:11212' % (threads, rep))

def run_memcached():
	with settings(host_string='asl1'):
		runbg('memcached -p 11212 -t 1')

def run_memaslap(run_time, clients):
	with settings(host_string='asl2'):
		with cd('libmemcached-1.0.18'):
			run('./clients/memaslap -s 10.0.0.12:11212 -T %d -c %d -o 0.9 -S %s -t %s > ../logs/microbench%d' 
					% (clients, clients, run_time, run_time, clients))

def run_memaslap_async(host, run_time, clients, series_number):
	with settings(host_string=host):
		with cd('libmemcached-1.0.18'):
			runbg('./clients/memaslap -s 10.0.0.12:11212 -T %d -c %d -o 0.9 -S %ss -t %ss' 
					% (clients, clients, run_time, run_time),
					'../logs/microbench%d_%d' % (clients, series_number))

def stop_middleware():
	with settings(host_string='asl11'):
		run('pkill -f middleware')

def stop_memcached():
	with settings(host_string='asl1'):
		run('pkill -f memcached')

def runbg(cmd, output_file=None, sockname="dtach"):
	if output_file:
		cmd = "/bin/bash -c '{} > {}'".format(cmd, output_file)
	else:
		cmd = "/bin/bash -c '{}'".format(cmd)
	return run('dtach -n `mktemp -u /tmp/%s.XXXX` %s'  % (sockname,cmd))

def run_experiments():
	run_time = '30s'
	max_clients = 32
	run_memcached()
	for clients in range(1, max_clients + 1):
		run_memaslap(run_time, clients)
	stop_memcached()

def run_double_experiments(series_number = 1):
	run_time = 30
	pause = 5
	max_clients = 64
	run_memcached()
	for clients in range(1, max_clients + 1):
		run_memaslap_async('asl2', run_time, clients, series_number)
		run_memaslap_async('asl3', run_time, clients, series_number)
		time.sleep(run_time + pause)
	stop_memcached()