# coding: utf8

@auth.requires_login()
def worker1():
    simulation_id = request.args(0)
    session_id = response.session_id
    scheduler.queue_task(floating_point_add,
                         task_name='floating_point_add',
                         pargs=[simulation_id,
                                str(auth.user.id),
                                str(session_id)])
    response.js = "$('#worker_1_queue').addClass('disabled');"
    response.flash = "Function floating_point_add scheduled"
    redirect(URL('plugin_cs_monitor', 'index'))
