
def update_elasticsearch(grouped_records):
    print('\n\nupdate_elasticsearch()')

    print('\n\nUPRN: {}'.format(grouped_records[0]))
    from pprint import pprint
    for i in grouped_records[1]:
        pprint(i._asdict(), width=1)
