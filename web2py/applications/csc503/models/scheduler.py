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


def floating_point_add(*args, **vars):
    print 'args=%s, vars=%s' % (args, vars)
    simulation_id = args[0]
    owner_id = args[1]
    session_id = args[2]
    # log_api_url = URL('default', 'api', args=['simulation_log'], user_signature=True, scheme=True)
    # plot_api_url = URL('default', 'api', args=['simulation_plot'], user_signature=True, scheme=True)
    log_api_url = URL('default', 'api', args=['simulation_log'], scheme=True)
    plot_api_url = URL('default', 'api', args=['simulation_plot'], scheme=True)
    module_folder = os.path.join(request.folder, 'modules/')
    temp_folder = os.path.join(request.folder, 'private/temp/')
    api_url = URL('default', 'api', scheme=True)
    status = subprocess.call([module_folder + 'floating_point_add.sh',  # $0
                              module_folder,                            # $1
                              api_url,                                  # $2
                              simulation_id,                            # $3
                              owner_id,                                 # $4
                              session_id])                              # $5
    # status = subprocess.call([module_folder + 'floating_point_add.sh',  # $0
    #                           module_folder,                            # $1
    #                           log_api_url,                              # $2
    #                           plot_api_url,                             # $3
    #                           temp_folder,                              # $4
    #                           simulation_id,                            # $5
    #                           user_id])                                 # $6
    return dict(status=status)