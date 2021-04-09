import os
import requests
import json
import datetime
import time
import itertools
import sys
import pandas as pd

from phrases import phrase_ids

END_TIMESTAMP = int(datetime.datetime(2021, 4, 1).timestamp())
EARLIEST_TIMESTAMP = 0

# Max value of the limit param. cf. https://www.reddit.com/r/pushshift/comments/ih66b8/difference_between_size_and_limit_and_are_they/
MAX_RESULTS_PER_REQUEST = 100

# If we get a response code other than 200, we will retry up to this many times,
# waiting 2, 4, 8... seconds between attempts
MAX_RETRIES = 8

MAX_REQUESTS_PER_TERM = 2000

CACHE_DIR = 'comment_data'

# This script draws some inspiration from https://github.com/Watchful1/Sketchpad/blob/master/postDownloader.py

COMMENT_ATTR_WHITELIST = set('body,created_utc,permalink,score,subreddit,author'.split(','))
def shake_comment_data(dat):
    """Given a jsondict of information about a comment, return a copy with only
    the fields we care about saving.
    """
    d = {k:v for k, v in dat.items() if k in COMMENT_ATTR_WHITELIST}
    return d

def load_extant(path):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def download_comments(term):
    outpath = os.path.join(CACHE_DIR, f'{term.replace(" ", "_")}.json')
    comments = load_extant(outpath)
    if len(comments) == 0:
        endpoint = END_TIMESTAMP
    else:
        endpoint = comments[-1]['created_utc'] - 1
    retries = 0
    while len(comments) < MAX_REQUESTS_PER_TERM * MAX_RESULTS_PER_REQUEST:
        if ' ' in term:
            querystring = '"' + term.replace(' ', '+') + '"'
        else:
            querystring = term
        url = f"https://api.pushshift.io/reddit/comment/search?limit={MAX_RESULTS_PER_REQUEST}&sort=desc&before={endpoint}&after={EARLIEST_TIMESTAMP}&q={querystring}"
        response = requests.get(url, headers={'User-Agent': "script by /u/halfeatenscone"})
        time.sleep(1)
        if response.status_code != 200:
            retries += 1
            if retries > MAX_RETRIES:
                sys.stderr.write(f"WARNING: aborting term {term} after max retries for url {url}\n")
                break
            wait = 2**retries
            time.sleep(wait)
            continue
        dat = response.json()
        results = dat['data']
        comments.extend([shake_comment_data(comm) for comm in results])
        if len(results) < MAX_RESULTS_PER_REQUEST:
            break

        endpoint = results[-1]['created_utc'] - 1
    else:
        sys.stderr.write(f"WARNING: quitting term {term} at t={endpoint} after reaching max requests\n")

    with open(outpath, 'w') as f:
        json.dump(comments, f, indent=0)

def main():
    for phrase_id in phrase_ids:
        term = phrase_id.replace('_', ' ')
        print(f"Dowloading comments for term {term!r}")
        download_comments(term)

if __name__ == '__main__':
    main()
