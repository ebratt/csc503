# -*- coding: utf-8 -*-
from plugin_tablescope import TableScope
from plugin_solidtable import SOLIDTABLE, OrderbySelector

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """

    # build the SOLIDTABLE
    orderby_selector = OrderbySelector([~db.simulation.simulation_date])
    # dataset = db(db.simulation.simulation_owner==auth.user)
    dataset = db((db.simulation.id==db.simulation_log.simulation) & (db.simulation.id==db.simulation_plot.simulation) & (db.simulation.simulation_owner == auth.user))
    scope = TableScope(dataset, db.simulation.algorithm, renderstyle=True)
    rows = scope.scoped_dataset.select(db.simulation.simulation_date,
                                       db.simulation.algorithm,
                                       db.simulation.input_data,
                                       db.simulation.simulation_result,
                                       db.simulation_log.log_content,
                                       db.simulation_plot.plot_content,
                                       orderby=orderby_selector.orderby())
    headers = {'simulation.simulation_date': {'selected': True},
               'simulation.algorithm': {'selected': False},
               'simulation.input_data': {'selected': False},
               'simulation.simulation_result': {'selected': False}
    }
    extracolumns = [{'label': A('Log', _href='#'),
                     'content': lambda row, rc: A('Download', _href='download/%s' % row.simulation_log.log_content)},
                    {'label': A('Plot', _href='#'),
                     'content': lambda row, rc: A('Download', _href='download/%s' % row.simulation_plot.plot_content)},
                    ]
    columns = [db.simulation.simulation_date,
               db.simulation.algorithm,
               db.simulation.input_data,
               db.simulation.simulation_result, extracolumns[0]]
    table = SOLIDTABLE(rows,
                       columns=columns,
                       extracolumns=extracolumns,
                       headers=headers,
                       orderby=orderby_selector,
                       renderstyle=True)
    return dict(sample_1=dict(table=table, scope=scope))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
