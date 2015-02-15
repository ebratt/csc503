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
                                       db.simulation_log.log_content,
                                       db.simulation_plot.plot_content,
                                       orderby=orderby_selector.orderby())
    headers = {'simulation.simulation_date': {'selected': True},
               'simulation.algorithm': {'selected': False},
               'simulation.input_data': {'selected': False}
    }
    extracolumns = [{'label': A('Log', _href='#'),
                     'content': lambda row, rc: A('Download', _href='download/%s' % row.simulation_log.log_content)},
                    {'label': A('Plot', _href='#'),
                     'content': lambda row, rc: A('Download', _href='download/%s' % row.simulation_plot.plot_content)},
                    ]
    columns = [db.simulation.simulation_date,
               db.simulation.algorithm,
               db.simulation.input_data,
               extracolumns[0]]
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


auth.settings.allow_basic_login = True
# @auth.requires_login()
@auth.requires_membership('api')
# @auth.requires_signature()
@request.restful()
def api():
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    def POST(table_name,**vars):
        return db[table_name].validate_and_insert(**vars)
    def PUT(table_name,record_id,**vars):
        return db(db[table_name]._id==record_id).update(**vars)
    def DELETE(table_name,record_id):
        return db(db[table_name]._id==record_id).delete()
    return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)


@auth.requires_membership("admin") # uncomment to enable security 
def list_users():
    btn = lambda row: A("Edit", _href=URL('manage_user', args=row.auth_user.id))
    db.auth_user.edit = Field.Virtual(btn)
    rows = db(db.auth_user).select()
    headers = ["ID", "Name", "Last Name", "Email", "Edit"]
    fields = ['id', 'first_name', 'last_name', "email", "edit"]
    table = TABLE(THEAD(TR(*[B(header) for header in headers])),
                  TBODY(*[TR(*[TD(row[field]) for field in fields]) \
                        for row in rows]))
    table["_class"] = "table table-striped table-bordered table-condensed"
    return dict(table=table)


@auth.requires_membership("admin") # uncomment to enable security 
def manage_user():
    user_id = request.args(0) or redirect(URL('list_users'))
    form = SQLFORM(db.auth_user, user_id).process()
    membership_panel = LOAD(request.controller,
                            'manage_membership.html',
                             args=[user_id],
                             ajax=True)
    return dict(form=form,membership_panel=membership_panel)


@auth.requires_membership("admin") # uncomment to enable security 
def manage_membership():
    user_id = request.args(0) or redirect(URL('list_users'))
    db.auth_membership.user_id.default = int(user_id)
    db.auth_membership.user_id.writable = False
    form = SQLFORM.grid(db.auth_membership.user_id == user_id,
                       args=[user_id],
                       searchable=False,
                       deletable=False,
                       details=False,
                       selectable=False,
                       csv=False,
                       user_signature=False)
    return form
