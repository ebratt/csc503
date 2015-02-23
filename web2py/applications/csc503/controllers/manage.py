# coding: utf8

@auth.requires_login()
def worker1():
    simulation_id = request.args(0)
    algorithm = request.args(1)
    log_level = request.args(2)
    session_id = response.session_id
    scheduler.queue_task(simulation,
                         task_name=algorithm,
                         scheduler_task_owner=auth.user.id,
                         pargs=[simulation_id,
                                str(auth.user.id),
                                str(session_id),
                                algorithm,
                                log_level])
    response.js = "$('#worker_1_queue').addClass('disabled');"
    session.flash = "%s scheduled" % algorithm
    redirect(URL('plugin_cs_monitor', 'index'))
