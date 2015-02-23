
def update_site_map(grouped_records):
    print('\n\nupdate_site_map()')

    print('\n\nUPRN: {}'.format(grouped_records[0]))
    from pprint import pprint
    for i in grouped_records[1]:
        pprint(i._asdict(), width=1)
