# -*- coding: utf-8 -*-
import random
import datetime

db.define_table('algorithm',
                Field('Name', 'string'),
                Field('Description', 'text'),
                format='%(Name)s')

db.define_table('input_data',
                Field('input_value', 'list:string'),
                Field('algorithms', 'list:reference algorithm'),
                Field('input_data_type', 'string', requires=IS_IN_SET(['int','list'])),
                Field('description', 'string'),
                format='%(input_value)s-%(description)s')

db.define_table('simulation',
                Field('simulation_date', 'datetime', writable=False, default=datetime.datetime.today()),
                Field('algorithm', 'reference algorithm'),
                Field('input_data', 'reference input_data'),
                Field('simulation_owner', 'reference auth_user', default=auth.user_id, readable=False),
                format='date: %(simulation_date)s; algorithm: %(algorithm)s')

db.define_table('simulation_log',
                Field('simulation', 'reference simulation'),
                Field('log_content', 'upload'),
                Field('log_owner', 'reference auth_user', default=auth.user_id),
                format='%(simulation)')

db.define_table('simulation_time_plot',
                Field('simulation', 'reference simulation'),
                Field('plot_content', 'upload'),
                Field('plot_owner', 'reference auth_user', default=auth.user_id),
                format='%(simulation)')

db.define_table('simulation_upload',
                Field('simulation', 'reference simulation'),
                Field('upload_content', 'upload'),
                Field('upload_owner', 'reference auth_user', default=auth.user_id),
                format='%(simulation)')


def check_initialize():
    if not db().select(db.auth_user.ALL).first():
        admin_id = db.auth_user.insert(
            password = db.auth_user.password.validate('admin')[0],
            email = 'admin@admin.com',
            first_name = 'admin',
            last_name = 'admin'
        )
        db.commit()
        api_id = db.auth_user.insert(
            password = db.auth_user.password.validate('pass')[0],
            email = 'api@api.com',
            first_name = 'api',
            last_name = 'api'
        )
        db.commit()
    if not db().select(db.auth_group.ALL).first():
        admin_group_id = db.auth_group.insert(role='admin',
                             description='reserved for admins')
        db.commit()
        api_group_id = db.auth_group.insert(role='api',
                             description='reserved for api calls')
        db.commit()
        db.auth_membership.insert(user_id = admin_id,
                                  group_id = admin_group_id)
        db.commit()
        db.auth_membership.insert(user_id = api_id,
                                  group_id = api_group_id)
        db.commit()

    # if the algorithm table is empty, populate it with data
    if not db().select(db.algorithm.ALL).first():
        desc = "Example taken from section 2.2.5 of An Introduction to Parallel "
        desc += "Programming Peter S. Pacheco University of San Francisco "
        desc += "Pacheco, Peter (2011-02-17). An Introduction to Parallel Programming "
        desc += "Elsevier Science. Kindle Edition."
        db.algorithm.insert(Name='floating_point_add',
                            Description=desc)
        db.commit()
        desc = "Example taken from Massimo Di Pierro "
        desc += "CSC503, DePaul University "
        db.algorithm.insert(Name='merge_sort',
                            Description=desc)
        db.commit()
        desc = "Not yet implemented "
        db.algorithm.insert(Name='bubble_sort',
                            Description=desc)
        db.commit()
        desc = "Not yet implemented "
        db.algorithm.insert(Name='differential_equation',
                            Description=desc)
        db.commit()

    # populate the table if it is empty
    if db(db.input_data).isempty():
        random.seed(12345)
        input_value = random.randint(0, 1000000)
        algorithms = db.executesql('SELECT id FROM algorithm where Name == "floating_point_add";')
        algorithms = [x for (x, ) in algorithms]
        description = 'Number of random integers to add'
        db.input_data.insert(input_value=input_value,
                             algorithms=algorithms,
                             input_data_type='int',
                             description=description)
        db.commit()
        input_value = [random.randint(0, 16) for r in xrange(16)]
        algorithms = db.executesql('SELECT id FROM algorithm where Name == "merge_sort" OR Name == "bubble_sort";')
        algorithms = [x for (x, ) in algorithms]
        description = 'List of things to sort'
        # algorithms = db((db.algorithm.Name=='merge_sort') | (db.algorithm.Name=='bubble_sort')).select().id
        db.input_data.insert(input_value=input_value,
                             algorithms=algorithms,
                             input_data_type='list',
                             description=description)
        db.commit()
        input_value = [chr(random.randint(97, 122)) for r in xrange(97, 123)] + \
                      [chr(random.randint(97, 103)) for r in xrange(97, 103)]
        description = 'List of things to sort'
        db.input_data.insert(input_value=input_value,
                             algorithms=algorithms,
                             input_data_type='list',
                             description=description)
        db.commit()
        algorithms = db.executesql('SELECT id FROM algorithm where Name == "differential_equation";')
        algorithms = [x for (x, ) in algorithms]
        description = 'Number of derivative steps'
        for i in xrange(10, 20):
            input_value = [i]
            db.input_data.insert(input_value=input_value,
                                 algorithms=algorithms,
                                 input_data_type='int',
                                 description=description)
            db.commit()



# do initialization check
# cache.ram('db_initialized', lambda: check_initialize())
cache.ram('db_initialized', lambda: check_initialize(), time_expire=None)