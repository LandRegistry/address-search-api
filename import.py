import argparse

from import_addressbase import import_csv


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Imports AddressBase CSV '
                                                 'files into elasticsearch.')
    parser.add_argument('filename', help='AddressBase CSV filename')
    parser.add_argument('-n', '--nodes', nargs='+',
                        help='<Required> Elasticsearch nodes (host[:port] '
                             'eg. "localhost:4900")',
                        required=True)
    args = parser.parse_args()

    import_csv(args.filename, args.nodes)

