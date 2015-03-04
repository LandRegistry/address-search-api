
from collections import namedtuple

# see: http://www.ordnancesurvey.co.uk/docs/technical-specifications/addressbase-premium-technical-specification-csv.pdf

Header = namedtuple('HeaderRecord', [
    'record_identifier', 'custodian_name', 'local_custodian_code',
    'process_date', 'volume_number', 'entry_date', 'time_stamp', 'version',
    'file_type']
)

BLPU = namedtuple('BLPU', [
    'record_identifier', 'change_type', 'pro_order', 'uprn', 'logical_status',
    'blpu_state', 'blpu_state_date', 'parent_uprn', 'x_coordinate',
    'y_coordinate', 'rpc', 'local_custodian_code', 'start_date', 'end_date',
    'last_update_date', 'entry_date', 'postal_address', 'postcode_locator',
    'multi_occ_count']
)

DPA = namedtuple('DPA', [
    'record_identifier', 'change_type', 'pro_order', 'uprn',
    'parent_addressable_uprn', 'rm_udprn', 'organisation_name',
    'department_name', 'sub_building_name', 'building_name', 'building_number',
    'dependent_thoroughfare_name', 'thoroughfare_name',
    'double_dependent_locality', 'dependent_locality', 'post_town', 'postcode',
    'postcode_type', 'welsh_dependent_thoroughfare_name',
    'welsh_thoroughfare_name', 'welsh_double_dependent_locality',
    'welsh_dependent_locality', 'welsh_post_town', 'po_box_number',
    'process_date', 'start_date', 'end_date', 'last_update_date', 'entry_date']
)
