# coding: utf8

@auth.requires_login()
def worker1():
    simulation_id = request.args(0)
    algorithm = request.args(1)
    session_id = response.session_id
    scheduler.queue_task(simulation,
                         task_name=algorithm,
                         pargs=[simulation_id,
                                str(auth.user.id),
                                str(session_id),
                                algorithm])
    response.js = "$('#worker_1_queue').addClass('disabled');"
    response.flash = "Function %s scheduled" % algorithm
    redirect(URL('plugin_cs_monitor', 'index'))
