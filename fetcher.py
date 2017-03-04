import json
import sys
from datetime import datetime

import pyopenstates
import re
import scrapelib

s = scrapelib.Scraper(requests_per_minute=10)


def serialize_datetime(obj):
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


def get_states():
    return ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'dc', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky',
            'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh',
            'ok', 'or', 'pa', 'pr', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy']


def get_sessions_for_state(state):
    return pyopenstates.get_metadata(state=state, fields='session_details')['session_details']


def get_reproductive_issues_bills(state):
    return pyopenstates.search_bills(state=state, subject='Reproductive Issues')


def stuff():
    bills = pyopenstates.search_bills(state='az', chamber='upper')
    first_ten_bills = bills[0:10]
    print('bill search in az', json.dumps(first_ten_bills, default=serialize_datetime))
    for bill in first_ten_bills:
        bill_details = pyopenstates.get_bill(uid=bill['id'])
        latest_version_text_url = bill_details['versions'][-1]['url']
        print('bill', bill['bill_id'], json.dumps(bill_details, default=serialize_datetime))
        print('text url', latest_version_text_url)


def get_latest_text_url(bill_details):
    if 'versions' in bill_details and len(bill_details['versions']) > 0 and 'url' in bill_details['versions'][-1]:
        return bill_details['versions'][-1]['url']


def search_bills_for_keywords(bills, keywords):
    bills_to_keywords = dict()
    index = 0
    for bill in bills:
        matched_keywords = search_for_keywords(bill['title'], keywords)
        bill_id = bill['id']
        print(bill_id, index, "of", len(bills))
        index += 1
        if len(matched_keywords) > 0:
            bills_to_keywords[bill_id] = matched_keywords
            print(bill_id, ":", matched_keywords, ",")
            continue
        bill_details = pyopenstates.get_bill(uid=bill_id)
        latest_text_url = get_latest_text_url(bill_details)
        if not latest_text_url:
            continue
        try:
            bill_full_text = s.get(latest_text_url).text
        except:
            print("error getting:" + latest_text_url, sys.exc_info()[0])
            continue
        matched_keywords = search_for_keywords(bill_full_text, keywords)
        if len(matched_keywords) > 0:
            bills_to_keywords[bill_id] = matched_keywords
            print(bill_id, ":", matched_keywords, ",")
    return bills_to_keywords


def search_for_keywords(text, keywords):
    matched_keywords = []
    for keyword in keywords:
        if re.search(keyword, text, re.IGNORECASE):
            matched_keywords.append(keyword)
    return matched_keywords


def main():
    relevant_bills = dict()
    with open('keywords.json', 'r') as keywords_file:
        keywords = json.load(keywords_file)
    for state in get_states():
        relevant_bills[state] = dict()
        for session in get_sessions_for_state(state).keys():
            relevant_bills[state][session] = dict()
            print(state, "session", session)
            bills = pyopenstates.search_bills(state=state, session=session, subject='Reproductive Issues')
            relevant_bills[state][session].update(search_bills_for_keywords(bills, keywords))
    print(json.dumps(relevant_bills, default=serialize_datetime))


if __name__ == '__main__':
    main()
    # stuff()
