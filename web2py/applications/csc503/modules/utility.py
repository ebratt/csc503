import logging


def check_args(argv):
    l = logging.getLogger('root')
    api_url = argv[1] or None
    if api_url is None:
        e = Exception('no api url!')
        l.log_a_value(e)
        raise Exception(e)
    simulation_id = int(argv[2]) or None
    if simulation_id is None:
        e = Exception('no simulation id!')
        l.log_a_value(e)
        raise Exception(e)
    owner_id = argv[3] or None
    if owner_id is None:
        e = Exception('no owner id!')
        l.log_a_value(e)
        raise Exception(e)
    session_id = argv[4] or None
    if session_id is None:
        e = Exception('no session id!')
        l.log_a_value(e)
        raise Exception(e)
    algorithm_name = argv[5] or None
    if algorithm_name is None:
        e = Exception('no algorithm name!')
        l.log_a_value(e)
        raise Exception(e)
    return dict(api_url=api_url,
                simulation_id=simulation_id,
                owner_id=owner_id,
                session_id=session_id,
                algorithm_name=algorithm_name)

def get_data(api_url, simulation_id):

    return dict('')