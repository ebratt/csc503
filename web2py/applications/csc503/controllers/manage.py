# coding: utf8

@auth.requires_login()
def worker1():
    scheduler.queue_task(floating_point_add, task_name='floating_point_add')
    response.js = "$('#worker_1_queue').addClass('disabled');"
    response.flash = "Function floating_point_add scheduled"
    redirect(URL('plugin_cs_monitor', 'index'))