# -*- coding: utf-8 -*-
import datetime

db.define_table('algorithm',
                Field('Name', 'string'),
                Field('Description', 'text'),
                format='%(Name)s')

db.define_table('simulation',
                Field('simulation_date', 'datetime', writable=False, default=datetime.datetime.today()),
                Field('algorithm', 'reference algorithm', required=True),
                Field('input_upload', 'upload', required=True),
                Field('log_level', 'string', required=True, requires=IS_IN_SET(['INFO', 'DEBUG']), default='INFO'),
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
            password=db.auth_user.password.validate('admin')[0],
            email='admin@admin.com',
            first_name='admin',
            last_name='admin'
        )
        db.commit()
        api_id = db.auth_user.insert(
            password=db.auth_user.password.validate('pass')[0],
            email='api@api.com',
            first_name='api',
            last_name='api'
        )
        db.commit()
    if not db().select(db.auth_group.ALL).first():
        admin_group_id = db.auth_group.insert(role='admin',
                                              description='reserved for admins')
        db.commit()
        api_group_id = db.auth_group.insert(role='api',
                                            description='reserved for api calls')
        db.commit()
        db.auth_membership.insert(user_id=admin_id,
                                  group_id=admin_group_id)
        db.commit()
        db.auth_membership.insert(user_id=api_id,
                                  group_id=api_group_id)
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


# do initialization check
# cache.ram('db_initialized', lambda: check_initialize())
cache.ram('db_initialized', lambda: check_initialize(), time_expire=None)