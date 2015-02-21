# -*- coding: utf-8 -*-
from gluon.storage import Storage
from plugin_cs_monitor.html_helpers import mybootstrap

response.files.append(URL('static', 'css/prettify.css'))
response.files.append(URL('static', 'js/prettify.js'))

@auth.requires_login()
def index():
    docs = Storage()
    docs.simulation = """
#### Select an algorithm and the input data. psim2web2py will submit a task to the web2py Scheduler. For example,
``
scheduler.queue_task(floating_point_add, task_name='floating_point_add')
``:python

Instructions:
 - Select the **Algorithm**
 - Select the **Input Upload** (must be compatible with the algorithm)
    -- for example, the floating point add algorithm expects the number of random
      doubles to add, so you must provide an integer value in the upload file
    -- the merge-sort algorithm expects a list of sortable elements, like chars or
      integers. They should be separated by commas in the upload file (just like a Python list).
 - Hit **Submit** (this will persist the data to the db)
 - Hit **Calculate** (this queues a task for the scheduler)
 - You will be re-directed to the Monitor and can view the status of the task
 - Wait a few seconds or hit Auto-Refresh

What you should see in the monitoring dashboard:
 - One worker is **ACTIVE**
 - One scheduler_task gets **QUEUED**, goes into **ASSIGNED**, then **RUNNING**, and then becomes **COMPLETED**
 - When the task is **RUNNING**, a scheduler_run record pops up (**RUNNING**)
 - When the task is **COMPLETED**, the scheduler_run record is updated to show a **COMPLETED** or **FAILED** or
   **TIMEOUT** status (the default timeout is 60 seconds).
    """

    form = SQLFORM(db.simulation,
                   fields=['algorithm', 'input_upload'],
                   submit_button='Calculate',
                   formstyle=mybootstrap)
    simulation_id = None
    algorithm = None
    # if form.process(keepvalues=True).accepted:
    if form.process(onvalidation=my_form_processing).accepted:
        simulation_id = form.vars.id
        algorithm_id = int(form.vars.algorithm)
        algorithm = db(db.algorithm.id==algorithm_id).select()[0].Name
        session.flash = 'Simulation created'
        redirect(URL('manage', 'worker1', args=[simulation_id, algorithm]))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(docs=docs, form=form, simulation_id=simulation_id, algorithm=algorithm)


def my_form_processing(form):
    algorithm_id = int(form.vars.algorithm)
    if form.vars.input_upload != '':
        return
    form.errors.input_upload = 'Please upload a file!'
