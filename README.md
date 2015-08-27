# Setup

To create a virtual env, run the following from a shell:

```
    mkvirtualenv -p /usr/bin/python3 address-search-api
    pip install -r requirements.txt
```

To run it, run the following from a shell:

```
    workon address-search-api
    python import.py /path/to/addressbase_file.csv -n localhost:4900
```
