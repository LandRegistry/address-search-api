import os
from typing import Dict, Union

CONFIG_DICT = {
    'DEBUG': False,
    'LOGGING': True,
    'LOGGING_CONFIG_FILE_PATH': os.environ['LOGGING_CONFIG_FILE_PATH'],
    'FAULT_LOG_FILE_PATH': os.environ['FAULT_LOG_FILE_PATH'],
    'ELASTIC_SEARCH_ENDPOINT': os.environ['ELASTIC_SEARCH_ENDPOINT'],
    'MAX_NUMBER_SEARCH_RESULTS': int(os.environ['MAX_NUMBER_SEARCH_RESULTS']),
    'SEARCH_RESULTS_PER_PAGE': int(os.environ['SEARCH_RESULTS_PER_PAGE']),
}  # type: Dict[str, Union[bool, str, int]]

settings = os.environ.get('SETTINGS')

if settings == 'dev':
    CONFIG_DICT['DEBUG'] = True
elif settings == 'test':
    CONFIG_DICT['LOGGING'] = False
    CONFIG_DICT['DEBUG'] = True
    CONFIG_DICT['TESTING'] = True
    CONFIG_DICT['FAULT_LOG_FILE_PATH'] = '/dev/null'
