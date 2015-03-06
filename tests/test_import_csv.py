import mock

from import_addressbase.import_csv import make_es_actions, make_es_mappings
from import_addressbase.record_types import DPA


def test_correct_action_for_insert():
    field_vals = ['I' if f == 'change_type' else f for f in DPA._fields]
    dpa = DPA(*field_vals)
    position = {'x': 12.34, 'y': 56.78}
    entry_datetime = '2015-03-05T12:00:00'
    actions = make_es_actions(dpa, position, entry_datetime)

    expected_actions = [
        {
            '_index': 'landregistry',
            '_type': 'propertyByPostcode',
            '_id': 'uprn',
            '_source': {
                'buildingName': 'building_name',
                'buildingNumber': 'building_number',
                'departmentName': 'department_name',
                'dependentLocality': 'dependent_locality',
                'dependentThoroughfareName': 'dependent_thoroughfare_name',
                'doubleDependentLocality': 'double_dependent_locality',
                'entryDatetime': '2015-03-05T12:00:00',
                'organisationName': 'organisation_name',
                'position': {'x': 12.34, 'y': 56.78},
                'postTown': 'post_town',
                'postcode': 'postcode',
                'subBuildingName': 'sub_building_name',
                'thoroughfareName': 'thoroughfare_name',
                'uprn': 'uprn',
            },
        },
    ]

    assert actions == expected_actions


def test_correct_action_for_update():
    field_vals = ['U' if f == 'change_type' else f for f in DPA._fields]
    dpa = DPA(*field_vals)
    position = {'x': 12.34, 'y': 56.78}
    entry_datetime = '2015-03-05T12:00:00'
    actions = make_es_actions(dpa, position, entry_datetime)

    expected_actions = [
        {
            '_op_type': 'update',
            '_index': 'landregistry',
            '_type': 'propertyByPostcode',
            '_id': 'uprn',
            'doc': {
                'buildingName': 'building_name',
                'buildingNumber': 'building_number',
                'departmentName': 'department_name',
                'dependentLocality': 'dependent_locality',
                'dependentThoroughfareName': 'dependent_thoroughfare_name',
                'doubleDependentLocality': 'double_dependent_locality',
                'entryDatetime': '2015-03-05T12:00:00',
                'organisationName': 'organisation_name',
                'position': {'x': 12.34, 'y': 56.78},
                'postTown': 'post_town',
                'postcode': 'postcode',
                'subBuildingName': 'sub_building_name',
                'thoroughfareName': 'thoroughfare_name',
                'uprn': 'uprn',
            },
        },
    ]

    assert actions == expected_actions


def test_correct_action_for_delete():
    field_vals = ['D' if f == 'change_type' else f for f in DPA._fields]
    dpa = DPA(*field_vals)
    position = {'x': 12.34, 'y': 56.78}
    entry_datetime = '2015-03-05T12:00:00'
    actions = make_es_actions(dpa, position, entry_datetime)

    expected_actions = [
        {
            '_op_type': 'delete',
            '_index': 'landregistry',
            '_type': 'propertyByPostcode',
            '_id': 'uprn',
        },
    ]

    assert actions == expected_actions


def test_mappings_made_correctly():
    with mock.patch('import_addressbase.import_csv.IndicesClient') as client:
        mock_put_mapping = client.return_value.put_mapping

        make_es_mappings(None)

        expected_body = {
            'propertyByPostcode': {
                'properties': {
                    'uprn': {'type': 'string', 'index': 'no'},
                    'organisationName': {'type': 'string', 'index': 'no'},
                    'departmentName': {'type': 'string', 'index': 'no'},
                    'subBuildingName': {'type': 'string', 'index': 'no'},
                    'buildingName': {'type': 'string', 'index': 'no'},
                    'buildingNumber': {'type': 'string', 'index': 'no'},
                    'dependentThoroughfareName': {'type': 'string',
                                                  'index': 'no'},
                    'thoroughfareName': {'type': 'string', 'index': 'no'},
                    'doubleDependentLocality': {'type': 'string',
                                                'index': 'no'},
                    'dependentLocality': {'type': 'string', 'index': 'no'},
                    'postTown': {'type': 'string', 'index': 'no'},
                    'postcode': {'type': 'string', 'index': 'not_analyzed'},
                    'entryDatetime': {'format': 'date_time_no_millis',
                                      'type': 'date', 'index': 'no'},
                }
            }
        }
        mock_put_mapping.assert_called_with(index='landregistry',
                                            body=expected_body,
                                            doc_type='propertyByPostcode')
