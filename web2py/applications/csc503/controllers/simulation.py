# -*- coding: utf-8 -*-
from gluon.storage import Storage

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
 - Select the **Input Data** (must be compatible with the algorithm)
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

    form = SQLFORM(db.simulation, fields=['algorithm', 'input_data'])
    simulation_id = None
    algorithm_id = None
    algorithm = None
    if form.process(keepvalues=True).accepted:
        simulation_id = form.vars.id
        algorithm_id = form.vars.algorithm
        algorithm = db(db.algorithm.id==algorithm_id).select()[0].Name
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(docs=docs, form=form, simulation_id=simulation_id, algorithm=algorithm)

