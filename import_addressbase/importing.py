#!/usr/bin/env python

from betterprint import pprint                  # type: ignore
from copy import deepcopy                       # type: ignore
import csv                                      # type: ignore
from elasticsearch import Elasticsearch         # type: ignore
from elasticsearch.client import IndicesClient  # type: ignore
from elasticsearch.helpers import bulk          # type: ignore
from itertools import groupby
import logging
import logging.config  # type: ignore
from operator import itemgetter  # type: ignore
from typing import Dict, Iterator, List, Union

from record_types import Header, BLPU, DPA

LOGGER = logging.getLogger(__name__)

INDEX_NAME = 'address-search-api-index'

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

ADDRESS_KEY_FIELDS = [
    'sub_building_name', 'building_name', 'building_number', 'dependent_thoroughfare_name',
    'thoroughfare_name', 'double_dependent_locality', 'dependent_locality', 'post_town', 'postcode',
]  # type: List[str]

TYPE_TO_INDEX_MAPPING = {
    'address_by_joined_fields': 'joined_fields',
    'address_by_postcode': 'postcode',
}  # type: Dict[str, str]


def make_es_mappings(client) -> None:
    no_index_properties = {
        'uprn': {'type': 'string', 'index': 'no'},
        'organisation_name': {'type': 'string', 'index': 'no'},
        'department_name': {'type': 'string', 'index': 'no'},
        'sub_building_name': {'type': 'string', 'index': 'not_analyzed'},
        'building_name': {'type': 'string', 'index': 'not_analyzed'},
        'building_number': {'type': 'integer', 'index': 'not_analyzed'},
        'dependent_thoroughfare_name': {'type': 'string', 'index': 'no'},
        'thoroughfare_name': {'type': 'string', 'index': 'not_analyzed'},
        'double_dependent_locality': {'type': 'string', 'index': 'no'},
        'dependent_locality': {'type': 'string', 'index': 'no'},
        'post_town': {'type': 'string', 'index': 'no'},
        'postcode': {'type': 'string', 'index': 'no'},
        'x_coordinate': {'type': 'float', 'index': 'no'},
        'y_coordinate': {'type': 'float', 'index': 'no'},
        'joined_fields': {'type': 'string', 'index': 'no'},
        'entry_datetime': {'type': 'date', 'format': 'date_time_no_millis', 'index': 'no'},
    }  # type: Dict[str, Dict[str, str]]

    def make_es_mapping(doc_type: str, index_field: str) -> Dict[str, Dict[str, Dict[str, Dict[str, str]]]]:
        mapping = {doc_type: {'properties': deepcopy(no_index_properties)}}  # type: Dict[str, Dict[str, Dict[str, Dict[str, str]]]]
        # postcode searches are exact, anything else is not
        mapping[doc_type]['properties'][index_field]['index'] = 'not_analyzed' if index_field == 'postcode' else 'analyzed'
        return mapping

    mapping_tuples = [(doc_type, make_es_mapping(doc_type, index_field)) for doc_type, index_field in TYPE_TO_INDEX_MAPPING.items()]
    for doc_type, mapping in mapping_tuples:
        IndicesClient(client).put_mapping(index=INDEX_NAME, doc_type=doc_type, body=mapping)


def make_es_actions(dpa: DPA, blpu: BLPU, entry_datetime: str) -> List[Dict[str, Union[str, Dict[str, Union[str, float]]]]]:
    dpa_dict = vars(dpa)
    joined_fields = ', '.join([dpa_dict[f] for f in ADDRESS_KEY_FIELDS if dpa_dict[f]])
    x_coord = 0.0
    y_coord = 0.0
    if blpu:
        x_coord = float(blpu.x_coordinate)
        y_coord = float(blpu.y_coordinate)
    doc = {
        'uprn': dpa.uprn,
        'organisation_name': dpa.organisation_name,
        'department_name': dpa.department_name,
        'sub_building_name': dpa.sub_building_name,
        'building_name': dpa.building_name,
        'building_number': dpa.building_number,
        'dependent_thoroughfare_name': dpa.dependent_thoroughfare_name,
        'thoroughfare_name': dpa.thoroughfare_name,
        'double_dependent_locality': dpa.double_dependent_locality,
        'dependent_locality': dpa.dependent_locality,
        'post_town': dpa.post_town,
        'postcode': dpa.postcode,
        'joined_fields': joined_fields,
        'x_coordinate': x_coord,
        'y_coordinate': y_coord,
        'entry_datetime': entry_datetime,
    }  # type: Dict[str, Union[str, float]]

    def make_action(doc_type: str) -> Dict[str, Union[str, Dict[str, Union[str, float]]]]:
        action_dict_cases = {
            INSERT: {'_op_type': 'index', '_index': INDEX_NAME, '_type': doc_type, '_id': dpa.uprn, '_source': doc},
            UPDATE: {'_op_type': 'update', '_index': INDEX_NAME, '_type': doc_type, '_id': dpa.uprn, 'doc': doc},
            DELETE: {'_op_type': 'delete', '_index': INDEX_NAME, '_type': doc_type, '_id': dpa.uprn},
        }  # type: Dict[str, Dict[str, Union[str, Dict[str, Union[str, float]]]]]
        return action_dict_cases[dpa.change_type]

    actions = [make_action(doctype) for doctype in TYPE_TO_INDEX_MAPPING.keys()]
    return actions


def get_action_dicts(csv_file) -> Iterator[Dict[str, Union[str, Dict[str, Union[str, float]]]]]:
    """A generator which yields elasticsearch action dicts for groups of records
    with one DPA and zero or one BPLU
    """
    data_reader = csv.reader(csv_file)
    entry_datetime = None  # type: str

    for _, group in groupby(data_reader, itemgetter(UPRN)):
        rows = list(group)
        if len(rows) == 1 and int(rows[0][RECORD_IDENTIFIER]) == HEADER_ID:
            header = Header(*rows[0])
            # we use 'date_time_no_millis' format: yyyy-MM-dd’T'HH:mm:ssZZ
            # we assume UTC (+00) as the spec doesn't specify a timezone
            entry_datetime = '{}T{}+00'.format(header.entry_date, header.time_stamp)

            continue

        blpu_list = []  # type: List[BLPU]
        dpa_list = []   # type: List[DPA]
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
            blpu = []
            if len(blpu_list) == 1:
                blpu = blpu_list[0]
            action_dicts = make_es_actions(dpa, blpu, entry_datetime)

            pprint(action_dicts, width=1)

            for action_dict in action_dicts:
                yield action_dict


def import_csv(csv_file: str, nodes: List[str]) -> None:
    client = Elasticsearch(nodes)
    # create index if it doesn't exist
    if INDEX_NAME not in client.indices.status()['indices']:
        doc_type = list(TYPE_TO_INDEX_MAPPING.keys())[0]
        client.index(index=INDEX_NAME, doc_type=doc_type, body={})
    try:
        make_es_mappings(client)
        action_dicts = get_action_dicts(csv_file)
        bulk(client, action_dicts)
    except Exception as e:
        LOGGER.error('An error occurred when processing a bulk update', exc_info=e)
