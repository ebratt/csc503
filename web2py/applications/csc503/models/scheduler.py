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
    module_folder = os.path.join(request.folder, 'modules/')
    private_folder = os.path.join(request.folder, 'private/')
    status = subprocess.call([module_folder + 'floating_point_add.sh', module_folder, private_folder])
    return dict(status=status)