from fabric.api import *
from fabric.context_managers import settings
import time

middleware_server = '10.0.0.11'

def deploy():
	local('git push')
	with settings(host_string='asl11'):
		with cd('asl-fall16-project'):
			run('git pull')
			run('ant')

def init_connections():
	for host_number in range(1, 12):
		with settings(host_string='asl%d' % host_number):
			run('cd .')

def clear_keys():
	for host_number in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
		local('ssh-keygen -f "/home/aleksander/.ssh/known_hosts" \
			-R matusiaaforaslvms%d.westeurope.cloudapp.azure.com' % host_number)

def run_memcached(host, additional = ''):
	with settings(host_string=host):
		runbg('memcached -p 11212 -t 1' + additional)

def stop_middleware():
	with settings(host_string='asl11'):
		run('pkill -f middleware')

def stop_memcached(host):
	with settings(host_string=host):
		run('sudo pkill -f memcached')

def runbg(cmd, output_file=None, log_file='/dev/null', sockname="dtach"):
	if output_file:
		cmd = "/bin/bash -c '{} > {} 2> {}'".format(cmd, output_file, log_file)
	else:
		cmd = "/bin/bash -c '{} > /dev/null 2> /dev/null'".format(cmd)
	return run('dtach -n `mktemp -u /tmp/%s.XXXX` %s'  % (sockname,cmd))

def run_memaslap_async(host, run_time, stats_time, clients, output, additional = '', cfg = 'max_throughput'):
	with settings(host_string=host):
		with cd('libmemcached-1.0.18'):
			runbg('./clients/memaslap -s %s:11212 -T %d -c %d -o 0.9 -S %ss -t %ss -F ../workloads/%s.cfg' 
					% (middleware_server, clients, clients, stats_time, run_time, cfg) + additional,
					output)