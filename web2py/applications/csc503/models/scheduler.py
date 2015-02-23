# coding: utf8
import time
from gluon.scheduler import Scheduler
import subprocess
import os
from gluon import current


scheduler = Scheduler(dbs)
s = current._scheduler
dbs = s.db
st = dbs.scheduler_task
sw = dbs.scheduler_worker
sr = dbs.scheduler_run
sd = dbs.scheduler_task_deps


def demo1(*args,**vars):
    print 'you passed args=%s and vars=%s' % (args, vars)
    time.sleep(5)
    print '50%'
    time.sleep(5)
    print '!clear!100%'
    return dict(a=1, b=2)


def simulation(*args, **vars):
    print 'args=%s, vars=%s' % (args, vars)
    simulation_id = args[0]
    owner_id = args[1]
    session_id = args[2]
    algorithm = args[3]
    log_level = args[4]
    module_folder = os.path.join(request.folder, 'modules/')
    api_url = URL('default', 'api', scheme=True)
    download_url = URL('default', 'download', scheme=True)
    status = subprocess.call([module_folder + 'simulation.sh',          # $0
                              module_folder,                            # $1
                              api_url,                                  # $2
                              download_url,                             # $3
                              simulation_id,                            # $4
                              owner_id,                                 # $5
                              session_id,                               # $6
                              algorithm,                                # $7
                              log_level])                               # $8
    return dict(status=status)