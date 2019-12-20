#!/usr/bin/env python3

import csv
import sys
import glob
import gzip
import json

from twarc.json2csv import get_row, get_headings

queries = [
    {
        "name": "Darren Seals",
        "screen_name": "KingDSeals",
        "user_id": "2747681903"
    },
    {
        "name": "Edward Crawford",
        "screen_name": "eyeFLOODpanties",
        "user_id": "84946406"
    },
    {
        "name": "Bassem Masri",
        "screen_name": "bassem_masri",
        "user_id": "2734647354"
    },
    {
        "name": "Deandre Joshua",
        "screen_name": None,
        "user_id": None
    },
    {
        "name": "Danye Jones",
        "screen_name": None,
        "user_id": None
    }
]

data_dirs = [
    {
        "name": "Beyond the Hashtags",
        "glob": "data/AE0A86DE-E17D-438E-BCDF-AA1F04851CAF/data/tweets/*.txt.gz"
    },
    {
        "name": "BlackLivesMatter",
        "glob": "data/4D41FEA7-9E85-45B8-9499-362212278CAB/data/*.json.gz",
    },
    {
        "name": "Ferguson Scrape",
        "glob": "data/D651C3F6-5619-4A42-A8BC-7C22B7A9A44A/data/*.json.gz",
    },
    {
        "name": "Ferguson",
        "glob": "data/fe28a093-d3f4-42d7-83ba-f5ba1b1cc765/data/*.json.gz"
    }
]

def main():
    out = csv.writer(open("results.csv", "w"))
    out.writerow(get_headings() + ['dataset', 'file', 'user_match', 'match_type'])
    for d in data_dirs:
        for f in glob.glob(d['glob']):
            sys.stdout.write('\n{}:'.format(f))
            sys.stdout.flush()
            process_file(d['name'], f, out)

def process_file(source, json_path, out):
    for line in gzip.open(json_path):
        try:
            tweet = json.loads(line)
        except:
            continue
        match = tweet_match(tweet)
        if match:
            sys.stdout.write('.')
            sys.stdout.flush()
            out.writerow(get_row(tweet) + [source, json_path] + match)

def tweet_match(t):
    for q in queries:

        # tweet by the user?
        if q['user_id'] == t['user']['id_str']:
            if t['in_reply_to_user_id_str']:
                return [q['name'], 'replied']
            elif t.get('retweeted_status') is not None:
                return [q['name'], 'retweeted']
            else:
                return [q['name'], 'posted']

        # someone replied to a tweet by the user?
        if q['user_id'] and q['user_id'] == t['in_reply_to_user_id_str']:
            return [q['name'], 'replied to']

        # user reweeted by someone else?
        rt = t.get('retweeted_status')
        if rt and q['user_id'] == rt['user']['id_str']:
            return [q['name'], 'user retweeted']

        # user mentioned by someone else?
        for u in t['entities'].get('user_mentions', []):
            if q['user_id'] == u['id_str']:
                return [q['name'], 'user mentioned']

        # someone mentioned them by name?
        text = t.get('text') or t.get('full_text')
        text = text.lower()
        if q['name'].lower() in text:
            return [q['name'], 'name mention']

    return None

if __name__ == "__main__":
    main()
