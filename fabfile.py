
from fabric.api import *
from fabric.context_managers import settings

env.use_ssh_config = True

@hosts('asl11')
def deploy():
	local('git push')
	run('cd asl-fall16-project')
	run('git pull')

@hosts('asl11')
def run_middleware():
	threads = 3
	rep = 1
	run('cd asl-fall16-project')
	runbg('java -jar ./dist/middleware-matusiaa.jar -I 10.0.0.4 -p 11212 -t %d -r %d -m 10.0.0.5:11212' % (threads, rep))

def run_memcached():
	with settings(host_string='asl1'):
		runbg('memcached -p 11212 -t 1')

def run_memaslap(time, clients):
	with settings(host_string='asl2'):
		with cd('libmemcached-1.0.18'):
			run('./clients/memaslap -s 10.0.0.12:11212 -T %d -c %d -o1 -S %s -t %s > ../logs/microbench%d' 
					% (clients, clients, time, time, clients))

@hosts('asl11')
def stop_middleware():
	run('pkill -f middleware')

def stop_memcached():
	with settings(host_string='asl1'):
		run('pkill -f memcached')


def runbg(cmd, sockname="dtach"):
    return run('dtach -n `mktemp -u /tmp/%s.XXXX` %s'  % (sockname,cmd))

def run_experiment():
	time = '30s'
	max_clients = 32
	run_memcached()
	for clients in range(1, max_clients + 1):
		run_memaslap(time, clients)
	stop_memcached()
