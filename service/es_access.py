from elasticsearch import Elasticsearch  # type: ignore
from elasticsearch_dsl import Search     # type: ignore
from typing import Any, Dict, List, Tuple, Union

from service import app

ELASTICSEARCH_ENDPOINT = app.config['ELASTIC_SEARCH_ENDPOINT']
MAX_NUMBER_SEARCH_RESULTS = app.config['MAX_NUMBER_SEARCH_RESULTS']
SEARCH_RESULTS_PER_PAGE = app.config['SEARCH_RESULTS_PER_PAGE']


def _get_start_and_end_indexes(page_number: int, page_size: int) -> Tuple[int, int]:
    start_index = page_number * page_size
    end_index = start_index + page_size
    return start_index, end_index


# TODO: write integration tests for this module
def get_addresses_for_postcode(postcode: str, page_number: int, page_size: int):
    search = create_search('address_by_postcode')
    query = search.query('term', postcode=postcode.upper()).sort(
        {'sub_building_name': {'missing': '_last'}},
        {'building_name': {'missing': '_last'}},
        {'building_number': {'missing': '_last'}},
        {'dependent_thoroughfare_name': {'missing': '_last'}},
        {'thoroughfare_name': {'missing': '_last'}},
    )
    start_index, end_index = _get_start_and_end_indexes(page_number, page_size)
    return query[start_index:end_index].execute().hits


def get_addresses_for_phrase(phrase: str, page_number: int, page_size: int):
    search = create_search('address_by_joined_fields')
    query = search.filter('term', joined_fields=phrase.lower()).sort(
        {'sub_building_name': {'missing': '_last'}},
        {'building_name': {'missing': '_last'}},
        {'building_number': {'missing': '_last'}},
        {'dependent_thoroughfare_name': {'missing': '_last'}},
        {'thoroughfare_name': {'missing': '_last'}},
    )
    start_index, end_index = _get_start_and_end_indexes(page_number, page_size)
    return query[start_index:end_index].execute().hits


def create_search(doc_type: str):
    client = Elasticsearch([ELASTICSEARCH_ENDPOINT])
    search = Search(using=client, index='address-search-api-index', doc_type=doc_type)
    search = search[0:MAX_NUMBER_SEARCH_RESULTS]
    return search


def get_info():
    return Elasticsearch([ELASTICSEARCH_ENDPOINT]).info()
