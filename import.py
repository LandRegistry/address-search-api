#!/usr/bin/env python

import csv
from itertools import groupby
from operator import itemgetter

from record_types import Header, BLPU, DPA
from update_properties.update_elasticsearch import update_elasticsearch
from update_properties.update_site_map import update_site_map


CSV_PATH = '/vagrant/apps/import-addressbase/abp-sample/SX9090_small.csv'
HEADER_ID = 10  # Header record                (contains entry date)
BLPU_ID = 21    # Basic Land and Property Unit (contains coordinates)
DPA_ID = 28     # Delivery Point Address       (contains addresses)


# common column name indexes
RECORD_IDENTIFIER = 0
CHANGE_TYPE = 1
CHANGE_TYPE_CODE = 2
UPRN = 3


def get_grouped_address_rows():
    """A generator which yields UPRN and BLPU/DPA tuples 
    see: http://www.ordnancesurvey.co.uk/docs/technical-specifications/addressbase-premium-technical-specification-csv.pdf
    """
    with open(CSV_PATH, 'r') as csv_file:
        data_reader = csv.reader(csv_file)

        rec_types = {BLPU_ID: BLPU, DPA_ID: DPA}

        for key, items in groupby(data_reader, itemgetter(UPRN)):
            filtered = []
            for item in items:
                rec_id = int(item[RECORD_IDENTIFIER])
                if rec_id in rec_types.keys():
                    filtered += [rec_types[rec_id](*item)]
            yield (key, filtered)


if __name__ == '__main__':
    record_groups = get_grouped_address_rows()
    for grouped_records in record_groups:
        update_elasticsearch(grouped_records)
        update_site_map(grouped_records)
