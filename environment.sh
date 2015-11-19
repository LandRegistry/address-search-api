#!/bin/sh
export SETTINGS='dev'
export LOGGING_CONFIG_FILE_PATH='logging_config.json'
export FAULT_LOG_FILE_PATH='/var/log/applications/address-search-api-fault.log'
export ELASTIC_SEARCH_ENDPOINT='http://localhost:9200'
export MAX_NUMBER_SEARCH_RESULTS=50
export PYTHONPATH=.
export SEARCH_RESULTS_PER_PAGE=20
export PORT='8002'
