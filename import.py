import argparse  # type: ignore

from config import CONFIG_DICT
from import_addressbase import import_csv
from zipfile import ZipFile  # type: ignore
import argparse  # type: ignore
import os  # type: ignore

ELASTICSEARCH_ENDPOINT = str(CONFIG_DICT['ELASTIC_SEARCH_ENDPOINT'])

def handle_zip_files_in_folder(path):

    for dir_entry in os.listdir(path):
        dir_entry_path = os.path.join(path, dir_entry)
        print('found: {}'.format(dir_entry_path))
        if not os.path.isfile(dir_entry_path):
            for inner_dir_entry in os.listdir(dir_entry_path):
                inner_dir_entry_path = os.path.join(dir_entry_path, inner_dir_entry)
                print('inner: {}'.format(inner_dir_entry_path))
                print('is file: {}'.format(os.path.isfile(inner_dir_entry_path)))
                print('extension: {}'.format(os.path.splitext(inner_dir_entry_path)[-1].lower()))
                if os.path.isfile(inner_dir_entry_path) and os.path.splitext(inner_dir_entry_path)[-1].lower() == ".zip":
                        print('file found {}'.format(inner_dir_entry_path))
                        zipfile = ZipFile(inner_dir_entry_path, 'r')
                        for name in zipfile.namelist():
                            data_file = zipfile.open(name).read()
                            print('file name: {}'.format(name))
                            print('Got to the end')
                            import_csv(data_file.decode("utf-8"), [ELASTICSEARCH_ENDPOINT])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Imports AddressBase CSV files into elasticsearch.')
    parser.add_argument('directory', help='AddressBase CSV filename')
    args = parser.parse_args()

    handle_zip_files_in_folder(args.directory)
