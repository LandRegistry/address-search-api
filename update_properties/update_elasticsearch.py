
def update_elasticsearch(address_dicts):
    for address_dict in address_dicts:
        print('\n\nUPRN: {}'.format(address_dict['uprn']))
        from pprint import pprint
        pprint(address_dict, width=1)
