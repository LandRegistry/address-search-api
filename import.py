import argparse  # type: ignore

from config import CONFIG_DICT
from import_addressbase import import_csv

ELASTICSEARCH_ENDPOINT = str(CONFIG_DICT['ELASTIC_SEARCH_ENDPOINT'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Imports AddressBase CSV files into elasticsearch.')
    parser.add_argument('filename', help='AddressBase CSV filename')
    args = parser.parse_args()

    import_csv(args.filename, [ELASTICSEARCH_ENDPOINT])
