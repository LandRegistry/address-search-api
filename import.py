import argparse  # type: ignore

from config import CONFIG_DICT
from import_addressbase import import_csv
from zipfile import ZipFile  # type: ignore
import argparse  # type: ignore
import os  # type: ignore
from io import StringIO  # type: ignore

ELASTICSEARCH_ENDPOINT = str(CONFIG_DICT['ELASTIC_SEARCH_ENDPOINT'])


# Method to read from a 2 level directory and grab multiple zip files
# Format expected:
# ----------directory1
# ----------------directory2
# --------------------addressbase_file.csv-2015.zip
# --------------------addressbase_file.csv-2014.zip
# ----------------directory3
# --------------------addressbase_file.csv-2013.zip
def handle_zip_files_in_folder(path):
    # This will iterate over 2 levels of folder structure looking for multiple zip files
    for dir_entry in os.listdir(path):
        dir_entry_path = os.path.join(path, dir_entry)
        if not os.path.isfile(dir_entry_path):
            for inner_dir_entry in os.listdir(dir_entry_path):
                inner_dir_entry_path = os.path.join(dir_entry_path, inner_dir_entry)
                # we only care about Address Base zip files so ignore everything else
                if os.path.isfile(inner_dir_entry_path) and os.path.splitext(inner_dir_entry_path)[-1].lower() == ".zip":
                    zipfile = ZipFile(inner_dir_entry_path, 'r')
                    # The zip file may have mulitple files in it (it shouldn't but could have) so loop over them
                    for name in zipfile.namelist():
                        # unzip the file, make sure it's in utf-8 format
                        data_file = (zipfile.open(name).read()).decode("utf-8")
                        # Then call the main import program with a StringIO file rather than a plain String.
                        import_csv(StringIO(data_file), [ELASTICSEARCH_ENDPOINT])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Imports AddressBase CSV files into elasticsearch.')
    parser.add_argument('directory', help='AddressBase CSV filename')
    args = parser.parse_args()

    handle_zip_files_in_folder(args.directory)
