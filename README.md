# address-search-api

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

## Run the tests

To run unit tests, cd into the address-search-api directory and run `lr-run-unit-tests`.
