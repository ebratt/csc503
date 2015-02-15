# -*- coding: utf-8 -*-
import random
import datetime

# db.define_table('algorithm',
#                 Field('Name', 'string'),
#                 Field('Description', 'text'),
#                 format='%(Name)s')
# # if the algorithm table is empty, populate it with data
# if db(db.algorithm).isempty():
#     desc =  "Example taken from section 2.2.5 of An Introduction to Parallel "
#     desc += "Programming Peter S. Pacheco University of San Francisco "
#     desc += "Pacheco, Peter (2011-02-17). An Introduction to Parallel Programming "
#     desc += "Elsevier Science. Kindle Edition."
#     db.algorithm.insert(Name='floating_point_add',
#                         Description=desc)

db.define_table('input_data',
                Field('input_value', 'list:string'),
                format='%(input_value)s')
if db(db.input_data).isempty():
    random.seed(12345)
    db.input_data.insert(input_value=random.randint(0, 10))
    db.input_data.insert(input_value=chr(random.randint(97, 122)))
    db.input_data.insert(input_value=[random.randint(0, 10) for r in xrange(10)])
    db.input_data.insert(input_value=[chr(random.randint(97, 122)) for r in xrange(97, 122)])

db.define_table('simulation',
                Field('simulation_date', 'datetime', writable=False, default=datetime.datetime.today()),
                Field('algorithm', requires=IS_IN_SET([(1, 'Floating Point Add'), (2, 'Merge-Sort'), (3, '2nd Derivative')])),
                Field('input_data', 'reference input_data'),
                Field('simulation_owner', 'reference auth_user', default=auth.user_id, readable=False),
                format='%(simulation_date)s-%(algorithm)s')
_algorithm_options = dict(db.simulation.algorithm.requires.options())
db.simulation.algorithm.represent = lambda v: _algorithm_options[v]
# db.simulation.algorithm.widget = SQLFORM.widgets.autocomplete(
#     request, db.algorithm.Name, limitby=(0, 10), min_length=2)

db.define_table('simulation_log',
                Field('simulation', 'reference simulation'),
                Field('log_content', 'upload'),
                Field('log_owner', 'reference auth_user', default=auth.user_id),
                format='%(simulation)')

db.define_table('simulation_plot',
                Field('simulation', 'reference simulation'),
                Field('plot_content', 'upload'),
                Field('plot_owner', 'reference auth_user', default=auth.user_id),
                format='%(simulation)')
