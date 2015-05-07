import os
import json
import math
import time

import requests


with open(os.path.join('private', 'apikey.txt')) as read_file:
    api_key = read_file.read().rstrip()

def json_from_url(base, params):
    """Parse and return a json file obtained from the specified url."""
    response = requests.get(base, params=params)
    return response.json()

def query_lincs_api(service, query = '', verbose = False, block_size = 500, api_version = 'a2', sleep = 1):
    """
    # LINCS API variables
    # http://api.lincscloud.org/

    service = 'pertinfo'
    """
    assert block_size <= 1000
    api_url = 'http://api.lincscloud.org/{}/{}'.format(api_version, service)
    url_data = {'q': query, 'l': block_size, 'sk': 0, 'user_key': api_key, 'c': 'true'}
    
    num_docs = json_from_url(api_url, url_data)['count']
    num_blocks = int(math.ceil(float(num_docs) / block_size))
    del url_data['c']
    if verbose:
        print('{} results: splitting query into {} chunks of {}.'.format(num_docs, num_blocks, block_size))
    
    results = list()
    for i in range(num_blocks):
        if verbose:
            print('Chunk {}/{}'.format(i + 1, num_blocks))
        url_data['sk'] =  i * block_size
        time.sleep(sleep)
        results += json_from_url(api_url, url_data)
    
    return results

