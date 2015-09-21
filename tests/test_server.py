from collections import namedtuple
import json
import mock
from service.server import app
from service import es_access

FakeElasticsearchHits = namedtuple('address_records', ['hits', 'total'])

EXPECTED_RESPONSE = {
    'data': {
        'addresses': [
            {
                'building_name': 'THE CYPRESS HOUSE',
                'building_number': '1',
                'department_name': '',
                'dependent_locality': '',
                'dependent_thoroughfare_name': '',
                'double_dependent_locality': '',
                'entry_datetime': '',
                'joined_fields': '1 THE CYPRESS HOUSE, GLENTHORNE ROAD, EXETER, EX4 4QU',
                'organisation_name': '',
                'post_town': 'EXETER',
                'postcode': 'EX4 4QU',
                'sub_building_name': '',
                'thoroughfare_name': 'GLENTHORNE ROAD',
                'uprn': '10023118807',
                'x_coordinate': 291124.22,
                'y_coordinate': 94250.89,
            },
            {
                'building_name': 'THE CYPRESS HOUSE',
                'building_number': '2',
                'department_name': '',
                'dependent_locality': '',
                'dependent_thoroughfare_name': '',
                'double_dependent_locality': '',
                'entry_datetime': '',
                'joined_fields': '2 THE CYPRESS HOUSE, GLENTHORNE ROAD, EXETER, EX4 4QU',
                'organisation_name': '',
                'post_town': 'EXETER',
                'postcode': 'EX4 4QU',
                'sub_building_name': '',
                'thoroughfare_name': 'GLENTHORNE ROAD',
                'uprn': '10023118807',
                'x_coordinate': 291124.22,
                'y_coordinate': 94250.89,
            },
        ],
        'page_number': 0,
        'page_size': 20,
        'total': 2,
    }
}


def _get_es_postcode_results(*house_numbers, total=None):
    total = len(house_numbers) if total is None else total
    return FakeElasticsearchHits([_get_es_postcode_result(num) for num in house_numbers], total)


def _get_es_postcode_result(house_number):
    return {
        '_source': {
            'building_name': 'THE CYPRESS HOUSE',
            'building_number': str(house_number),
            'department_name': '',
            'dependent_locality': '',
            'dependent_thoroughfare_name': '',
            'double_dependent_locality': '',
            'entry_datetime': '',
            'joined_fields': '{} THE CYPRESS HOUSE, GLENTHORNE ROAD, EXETER, EX4 4QU'.format(house_number),
            'organisation_name': '',
            'post_town': 'EXETER',
            'postcode': 'EX4 4QU',
            'sub_building_name': '',
            'thoroughfare_name': 'GLENTHORNE ROAD',
            'uprn': '10023118807',
            'x_coordinate': 291124.22,
            'y_coordinate': 94250.89,
        }
    }


@mock.patch.object(es_access, 'get_addresses_for_postcode', return_value=_get_es_postcode_results(1, 2))
def test_search_results_using_postcode(mock_es_access):
    postcode = 'EX4 4QU'
    page_number = 0
    page_size = 20
    response = app.test_client().get('/search?postcode=EX4 4QU')

    mock_es_access.assert_called_once_with(postcode, page_number, page_size)

    json_body = json.loads(response.data.decode())
    assert json_body == EXPECTED_RESPONSE
