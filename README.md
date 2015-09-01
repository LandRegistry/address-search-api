# address-search-api

This is the repo for the Address Search API service. It is written in Python, with the Flask framework.

## Setup

To create a virtual env, run the following from a shell:

```
    mkvirtualenv -p /usr/bin/python3 address-search-api
    pip install -r requirements.txt
    pip install -r requirements_test.txt
```

## Importing data

To import data, run the following from a shell:

```
    workon address-search-api
    source environment.sh
    python import.py /path/to/addressbase_file.csv
```

## Deleting the index

During development it's occasionally useful to delete the elasticsearch index. To do so, use this command:

curl -XDELETE $ELASTIC_SEARCH_ENDPOINT/landregistry

## Run the server

### Run in dev mode

To run the server in dev mode, execute the following command:

    ./run_flask_dev.sh

### Run using gunicorn

To run the server using gunicorn, activate your virtual environment and execute the following commands:

    pip install gunicorn
    gunicorn -p /tmp/gunicorn.pid service.server:app -c gunicorn_settings.py

## Run the tests

To run unit tests, cd into the address-search-api directory and run `lr-run-unit-tests`.
