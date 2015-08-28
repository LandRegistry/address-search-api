#!/usr/bin/env python

import csv
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from itertools import groupby
from operator import itemgetter

from import_addressbase.record_types import Header, BLPU, DPA


INDEX_NAME = 'landregistry'

HEADER_ID = 10  # Header record                (contains entry date)
BLPU_ID = 21    # Basic Land and Property Unit (contains coordinates)
DPA_ID = 28     # Delivery Point Address       (contains addresses)

# the record identifier column index is common to all record types
RECORD_IDENTIFIER = 0
# these column indexes are common to the other record types we're interested in
CHANGE_TYPE = 1
CHANGE_TYPE_CODE = 2
UPRN = 3

# change_type values
INSERT = 'I'
UPDATE = 'U'
DELETE = 'D'

ADDRESS_KEY_FIELDS = ['organisation_name', 'sub_building_name', 'building_name',
                      'building_number', 'dependent_thoroughfare_name',
                      'thoroughfare_name', 'double_dependent_locality',
                      'dependent_locality', 'post_town', 'postcode']

TYPE_TO_INDEX_MAPPING = {
    'propertyByPostcode': 'postcode',
}


def make_es_mappings(client):
    no_index_properties = {
        'uprn': {'type': 'string', 'index': 'no'},
        'organisationName': {'type': 'string', 'index': 'no'},
        'departmentName': {'type': 'string', 'index': 'no'},
        'subBuildingName': {'type': 'string', 'index': 'no'},
        'buildingName': {'type': 'string', 'index': 'no'},
        'buildingNumber': {'type': 'string', 'index': 'no'},
        'dependentThoroughfareName': {'type': 'string', 'index': 'no'},
        'thoroughfareName': {'type': 'string', 'index': 'no'},
        'doubleDependentLocality': {'type': 'string', 'index': 'no'},
        'dependentLocality': {'type': 'string', 'index': 'no'},
        'postTown': {'type': 'string', 'index': 'no'},
        'postcode': {'type': 'string', 'index': 'no'},
        'entryDatetime': {'type': 'date',
                          'format': 'date_time_no_millis',
                          'index': 'no'},
    }

    def make_es_mapping(doc_type, index_field):
        mapping = {
            doc_type: {'properties': no_index_properties}
        }
        mapping[doc_type]['properties'][index_field]['index'] = 'not_analyzed'
        data = IndicesClient(client).put_mapping(index=INDEX_NAME,
                                                 doc_type=doc_type,
                                                 body=mapping)

    for doc_type, index_field in TYPE_TO_INDEX_MAPPING.items():
        make_es_mapping(doc_type, index_field)


def make_es_actions(dpa, position, entry_datetime):
    doc = {
        'uprn': dpa.uprn,
        'organisationName': dpa.organisation_name,
        'departmentName': dpa.department_name,
        'subBuildingName': dpa.sub_building_name,
        'buildingName': dpa.building_name,
        'buildingNumber': dpa.building_number,
        'dependentThoroughfareName': dpa.dependent_thoroughfare_name,
        'thoroughfareName': dpa.thoroughfare_name,
        'doubleDependentLocality': dpa.double_dependent_locality,
        'dependentLocality': dpa.dependent_locality,
        'postTown': dpa.post_town,
        'postcode': dpa.postcode,
        'position': position,
        'entryDatetime': entry_datetime,
    }

    def make_action(doc_type):
        if dpa.change_type == INSERT:
            action_dict = {
                '_index': INDEX_NAME,
                '_type': doc_type,
                '_id': dpa.uprn,
                '_source': doc,
            }
        elif dpa.change_type == UPDATE:
            action_dict = {
                '_op_type': 'update',
                '_index': INDEX_NAME,
                '_type': doc_type,
                '_id': dpa.uprn,
                'doc': doc,
            }
        elif dpa.change_type == DELETE:
            action_dict = {
                '_op_type': 'delete',
                '_index': INDEX_NAME,
                '_type': doc_type,
                '_id': dpa.uprn,
            }
        return action_dict

    actions = [make_action(doctype) for doctype in TYPE_TO_INDEX_MAPPING.keys()]
    return actions


def get_action_dicts(filename):
    """A generator which yields elasticsearch action dicts for groups of records
    with one DPA and zero or one BPLU
    """
    with open(filename, 'r') as csv_file:
        data_reader = csv.reader(csv_file)

        entry_datetime = None

        for _, group in groupby(data_reader, itemgetter(UPRN)):
            rows = list(group)
            if (len(rows) == 1 and
                    int(rows[0][RECORD_IDENTIFIER]) == HEADER_ID):
                header = Header(*rows[0])
                # we use 'date_time_no_millis' format: yyyy-MM-dd’T'HH:mm:ssZZ
                # we assume UTC (+00) as the spec doesn't specify a timezone
                entry_datetime = '{}T{}+00'.format(header.entry_date,
                                                   header.time_stamp)

                continue

            blpu_list = []
            dpa_list = []
            # create namedtuples from each line
            for row in rows:
                rec_type = int(row[RECORD_IDENTIFIER])
                # create a record using the values in the row
                if rec_type == BLPU_ID:
                    blpu_list += [BLPU(*row)]
                elif rec_type == DPA_ID:
                    dpa_list += [DPA(*row)]

            # we must have one DPA and zero or one BPLU
            if len(dpa_list) == 1 and len(blpu_list) in [0, 1]:
                dpa = dpa_list[0]
                position = None
                if len(blpu_list) == 1:
                    blpu = blpu_list[0]
                    position = {
                        'x': float(blpu.x_coordinate),
                        'y': float(blpu.y_coordinate)
                    }
                action_dicts = make_es_actions(dpa, position, entry_datetime)

                # TODO: remove debug print statement
                from pprint import pprint
                pprint(action_dicts, width=1)

                for action_dict in action_dicts:
                    yield action_dict


def import_csv(filename, nodes):
    client = Elasticsearch(nodes)
    # create index if it doesn't exist
    doc_type = list(TYPE_TO_INDEX_MAPPING.keys())[0]
    client.index(index=INDEX_NAME, doc_type=doc_type, body={})
    make_es_mappings(client)
    action_dicts = get_action_dicts(filename)
    bulk(client, action_dicts)
