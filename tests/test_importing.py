from collections import namedtuple
import mock

from import_addressbase import make_es_actions, make_es_mappings
from record_types import DPA

BLPU_COORDINATES_ONLY = namedtuple('BLPU_coordinates_only', ['x_coordinate', 'y_coordinate'])


def test_correct_action_for_insert():
    field_vals = ['I' if f == 'change_type' else f for f in DPA._fields]
    dpa = DPA(*field_vals)
    blpu = BLPU_COORDINATES_ONLY(x_coordinate=12.34, y_coordinate=56.78)
    entry_datetime = '2015-03-05T12:00:00'
    actions = make_es_actions(dpa, blpu, entry_datetime)

    expected_actions = [
        {
            '_op_type': 'index',
            '_index': 'address-search-api-index',
            '_type': 'address_by_joined_fields',
            '_id': 'uprn',
            '_source': {
                'building_name': 'building_name',
                'building_number': 'building_number',
                'department_name': 'department_name',
                'dependent_locality': 'dependent_locality',
                'dependent_thoroughfare_name': 'dependent_thoroughfare_name',
                'double_dependent_locality': 'double_dependent_locality',
                'entry_datetime': '2015-03-05T12:00:00',
                'joined_fields': 'sub_building_name, building_name, building_number, dependent_thoroughfare_name, thoroughfare_name, double_dependent_locality, dependent_locality, post_town, postcode',
                'postcode': 'postcode',
                'organisation_name': 'organisation_name',
                'post_town': 'post_town',
                'sub_building_name': 'sub_building_name',
                'thoroughfare_name': 'thoroughfare_name',
                'uprn': 'uprn',
                'x_coordinate': 12.34,
                'y_coordinate': 56.78,
            },
        },
        {
            '_op_type': 'index',
            '_index': 'address-search-api-index',
            '_type': 'address_by_postcode',
            '_id': 'uprn',
            '_source': {
                'building_name': 'building_name',
                'building_number': 'building_number',
                'department_name': 'department_name',
                'dependent_locality': 'dependent_locality',
                'dependent_thoroughfare_name': 'dependent_thoroughfare_name',
                'double_dependent_locality': 'double_dependent_locality',
                'entry_datetime': '2015-03-05T12:00:00',
                'joined_fields': 'sub_building_name, building_name, building_number, dependent_thoroughfare_name, thoroughfare_name, double_dependent_locality, dependent_locality, post_town, postcode',
                'postcode': 'postcode',
                'organisation_name': 'organisation_name',
                'post_town': 'post_town',
                'sub_building_name': 'sub_building_name',
                'thoroughfare_name': 'thoroughfare_name',
                'uprn': 'uprn',
                'x_coordinate': 12.34,
                'y_coordinate': 56.78,
            },
        },
    ]

    assert len(actions) == len(expected_actions)
    assert all(action in expected_actions for action in actions)


def test_correct_action_for_update():
    field_vals = ['U' if f == 'change_type' else f for f in DPA._fields]
    dpa = DPA(*field_vals)
    blpu = BLPU_COORDINATES_ONLY(x_coordinate=12.34, y_coordinate=56.78)
    entry_datetime = '2015-03-05T12:00:00'
    actions = make_es_actions(dpa, blpu, entry_datetime)

    expected_actions = [
        {
            '_op_type': 'update',
            '_index': 'address-search-api-index',
            '_type': 'address_by_joined_fields',
            '_id': 'uprn',
            'doc': {
                'building_name': 'building_name',
                'building_number': 'building_number',
                'department_name': 'department_name',
                'dependent_locality': 'dependent_locality',
                'dependent_thoroughfare_name': 'dependent_thoroughfare_name',
                'double_dependent_locality': 'double_dependent_locality',
                'entry_datetime': '2015-03-05T12:00:00',
                'joined_fields': 'sub_building_name, building_name, building_number, dependent_thoroughfare_name, thoroughfare_name, double_dependent_locality, dependent_locality, post_town, postcode',
                'postcode': 'postcode',
                'organisation_name': 'organisation_name',
                'post_town': 'post_town',
                'sub_building_name': 'sub_building_name',
                'thoroughfare_name': 'thoroughfare_name',
                'uprn': 'uprn',
                'x_coordinate': 12.34,
                'y_coordinate': 56.78,
            },
        },
        {
            '_op_type': 'update',
            '_index': 'address-search-api-index',
            '_type': 'address_by_postcode',
            '_id': 'uprn',
            'doc': {
                'building_name': 'building_name',
                'building_number': 'building_number',
                'department_name': 'department_name',
                'dependent_locality': 'dependent_locality',
                'dependent_thoroughfare_name': 'dependent_thoroughfare_name',
                'double_dependent_locality': 'double_dependent_locality',
                'entry_datetime': '2015-03-05T12:00:00',
                'joined_fields': 'sub_building_name, building_name, building_number, dependent_thoroughfare_name, thoroughfare_name, double_dependent_locality, dependent_locality, post_town, postcode',
                'postcode': 'postcode',
                'organisation_name': 'organisation_name',
                'post_town': 'post_town',
                'sub_building_name': 'sub_building_name',
                'thoroughfare_name': 'thoroughfare_name',
                'uprn': 'uprn',
                'x_coordinate': 12.34,
                'y_coordinate': 56.78,
            },
        },
    ]

    assert len(actions) == len(expected_actions)
    assert all(action in expected_actions for action in actions)


def test_correct_action_for_delete():
    field_vals = ['D' if f == 'change_type' else f for f in DPA._fields]
    dpa = DPA(*field_vals)
    blpu = BLPU_COORDINATES_ONLY(x_coordinate=12.34, y_coordinate=56.78)
    entry_datetime = '2015-03-05T12:00:00'
    actions = make_es_actions(dpa, blpu, entry_datetime)

    expected_actions = [
        {
            '_op_type': 'delete',
            '_index': 'address-search-api-index',
            '_type': 'address_by_joined_fields',
            '_id': 'uprn',
        },
        {
            '_op_type': 'delete',
            '_index': 'address-search-api-index',
            '_type': 'address_by_postcode',
            '_id': 'uprn',
        },
    ]

    assert len(actions) == len(expected_actions)
    assert all(action in expected_actions for action in actions)


def miss_out_test_mappings_made_correctly():
    with mock.patch('import_addressbase.importing.IndicesClient') as client:
        mock_put_mapping = client.return_value.put_mapping

        make_es_mappings(None)

        expected_body = {
            'address_by_postcode': {
                'properties': {
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
                    'postcode': {'type': 'string', 'index': 'not_analysed'},
                    'x_coordinate': {'type': 'float', 'index': 'no'},
                    'y_coordinate': {'type': 'float', 'index': 'no'},
                    'joined_fields': {'type': 'string', 'index': 'no'},
                    'entry_datetime': {'type': 'date', 'format': 'date_time_no_millis', 'index': 'no'}
                }
            }
        }
        mock_put_mapping.assert_any_call(index='address-search-api-index', body=expected_body, doc_type='address_by_postcode')

        expected_body2 = {
            'address_by_joined_fields': {
                'properties': {
                    'uprn': {'type': 'string', 'index': 'no'},
                    'organisation_name': {'type': 'string', 'index': 'no'},
                    'department_name': {'type': 'string', 'index': 'no'},
                    'sub_building_name': {'type': 'string', 'index': 'not_analyzed'},
                    'building_name': {'type': 'string', 'index': 'not_analyzed'},
                    'building_number': {'type': 'string', 'index': 'not_analyzed'},
                    'dependent_thoroughfare_name': {'type': 'string', 'index': 'no'},
                    'thoroughfare_name': {'type': 'string', 'index': 'not_analyzed'},
                    'double_dependent_locality': {'type': 'string', 'index': 'no'},
                    'dependent_locality': {'type': 'string', 'index': 'no'},
                    'post_town': {'type': 'string', 'index': 'no'},
                    'postcode': {'type': 'string', 'index': 'no'},
                    'joined_fields': {'type': 'string', 'index': 'analyzed'},
                    'x_coordinate': {'type': 'float', 'index': 'no'},
                    'y_coordinate': {'type': 'float', 'index': 'no'},
                    'entry_datetime': {'format': 'date_time_no_millis', 'type': 'date', 'index': 'no'},
                }
            },
        }
        mock_put_mapping.assert_any_call(index='address-search-api-index', body=expected_body2, doc_type='address_by_joined_fields')
