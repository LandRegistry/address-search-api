__author__ = 'russw'

from zipfile import ZipFile  # type: ignore
import argparse  # type: ignore
import os  # type: ignore


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
                            print(data_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Imports AddressBase CSV files into elasticsearch.')
    parser.add_argument('directory', help='AddressBase folder that contains the zip files')
    args = parser.parse_args()

    handle_zip_files_in_folder(args.directory)
