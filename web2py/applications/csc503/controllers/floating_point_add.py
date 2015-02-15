# -*- coding: utf-8 -*-
from gluon.storage import Storage

response.files.append(URL('static', 'css/prettify.css'))
response.files.append(URL('static', 'js/prettify.js'))

@auth.requires_login()
def index():
    docs = Storage()
    docs.floating_point_add = """
#### Floating Point Addition

TODO: NEED TO PUT A FORM() HERE TO CAPTURE INPUT

``
scheduler.queue_task(floating_point_add, task_name='floating_point_add')
``:python

Instructions:
 - Hit "Calculate"
 - Open another browser, login as 'admin,' and monitor the task
 - Wait a few seconds

What you should see in the monitoring dashboard:
 - one worker is **ACTIVE**
 - one scheduler_task gets **QUEUED**, goes into **RUNNING** for a while and then becomes **COMPLETED**
 - when the task is **RUNNING**, a scheduler_run record pops up (**RUNNING**)
 - When the task is **COMPLETED**, the scheduler_run record is updated to show a **COMPLETED** status.
    """
    # need a form to capture the simulation information
    form = SQLFORM(db.simulation, fields=['algorithm', 'input_data'])
    simulation_id = None
    if form.process(keepvalues=True).accepted:
        simulation_id = form.vars.id
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'

    return dict(docs=docs, form=form, simulation_id=simulation_id)

