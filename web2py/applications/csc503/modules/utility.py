import logging
import requests                                 # to call api
from requests.auth import HTTPBasicAuth         # to authenticate
import os


def check_args(argv):
    api_url = argv[1] or None
    if api_url is None:
        e = Exception('no api url!')
        raise Exception(e)
    simulation_id = int(argv[2]) or None
    if simulation_id is None:
        e = Exception('no simulation id!')
        raise Exception(e)
    owner_id = argv[3] or None
    if owner_id is None:
        e = Exception('no owner id!')
        raise Exception(e)
    session_id = argv[4] or None
    if session_id is None:
        e = Exception('no session id!')
        raise Exception(e)
    algorithm_name = argv[5] or None
    if algorithm_name is None:
        e = Exception('no algorithm name!')
        raise Exception(e)
    return api_url, simulation_id, owner_id, session_id, algorithm_name

def get_data(api_url, simulation_id):
    auth = HTTPBasicAuth('api@api.com', 'pass')     # TODO: change this in prod
    sim_input_get = requests.get(api_url + '/simulation/id/' +
                                 str(simulation_id) +
                                 '/input_data.json',
                                 auth=auth)
    import json
    sim_input_json = json.loads(sim_input_get.text)
    input_data_id = sim_input_json['content'][0]['input_data']
    input_data_get = requests.get(api_url +
                                  '/input-data/id/' +       # why input-id?
                                  str(input_data_id) +
                                  '/input_value.json',
                                  auth=auth)
    input_json = json.loads(input_data_get.text)
    try:
        input_data = int(input_json['content'][0]['input_value'][0])
    except:
        raise Exception('invalid input data')
    return input_data, auth


def setup_files(simulation_id, owner_id, session_id, algorithm_name):
    logfile = str(simulation_id) + '_' + \
              str(owner_id) + '_' + \
              str(session_id) + '_' + \
              '%s.log' % algorithm_name
    pngfilename = str(simulation_id) + '_' + \
                  str(owner_id) + '_' + \
                  str(session_id) + '_' + \
                  '%s.png' % algorithm_name
    trajectorypngfilename = str(simulation_id) + '_' + \
                  str(owner_id) + '_' + \
                  str(session_id) + '_' + \
                  '%s.png' % 'trajectory'
    return logfile, pngfilename, trajectorypngfilename


def make_requests(api_url, auth, log_files, plot_files, upload_files, log_payload, plot_payload, upload_payload):
    log_r = requests.post(api_url + '/simulation_log/', data=log_payload, files=log_files, auth=auth)
    plot_r = requests.post(api_url + '/simulation_time_plot/', data=plot_payload, files=plot_files, auth=auth)
    upload_r = requests.post(api_url + '/simulation_upload/', data=upload_payload, files=upload_files, auth=auth)
    return log_r, plot_r, upload_r


def remove_files(logfile, pngfilename, trajectorypngfilename):
    os.remove(logfile)
    os.remove(pngfilename)
    os.remove(trajectorypngfilename)