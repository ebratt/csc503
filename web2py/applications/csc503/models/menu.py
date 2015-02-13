# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('psim',SPAN(2),'web',SPAN(2),'py'),XML('&trade;&nbsp;'),
                  _class="brand",_href=URL('default', 'index'))
# response.title = request.application.replace('_',' ').title()
# response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'
response.meta.author = 'Eric Bratt <eric_bratt@yahoo.com>'
response.title = 'psim2web2py'
response.subtitle = '1.0.0'
response.static_version = '1.0.0'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]
response.menu += [
    (T('Monitor'), False, URL('plugin_cs_monitor', 'index'), [])
]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (SPAN('admin', _class='highlighted'), False, URL('admin', 'default'), [
        (T('My Sites'), False, URL('admin', 'default', 'site')),
        (T('This App'), False, URL('admin', 'default', 'design/%s' % app))]
        )]
if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu() 
