from datetime import datetime

import pyopenstates
import json


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


if __name__ == '__main__':
    bills = pyopenstates.search_bills(state='ca', chamber='upper')
    first_ten_bills = bills[0:10]
    print('bill search in ca', json.dumps(first_ten_bills, default=serialize_datetime))
    for bill in first_ten_bills:
        bill_details = pyopenstates.get_bill(uid=bill['id'])
        latest_version_text_url = bill_details['versions'][-1]['url']
        print('bill', bill['bill_id'], json.dumps(bill_details, default=serialize_datetime))
        print('text url', latest_version_text_url)
