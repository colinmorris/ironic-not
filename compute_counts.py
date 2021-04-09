"""Use raw json comment data to create a csv of (all-time) counts per term.
Takes care of the following details:
    - Filtering comments which should be ignored e.g. because the target term
      occurs as part of a URL, or a reference to a subreddit name.
    - Extrapolating counts for high-frequency terms for which we have sampled
      comment data.

TODO: Consider adding (optionally?) columns related to munging:
    - raw count (w/o any filtering or scaling)
    - whether count is extrapolated based on sampling
    - number of comments filtered
might be useful for debugging
"""
import re
import os
import json
import itertools
from collections import defaultdict
import argparse

from phrases import phrase_ids


RAW_DIR = 'comment_data'

def tokens_having_term(text, term):
    """Case insensitive."""
    # We also split on square brackets to account for markdown formatting (don't want link text to be mingled with url)
    tokens = re.split('[\s\[\]]', text)
    for token in tokens:
        if term in token.lower():
            yield token


def is_valid_comment(comment, term):
    """Return whether the given comment should contribute to our cuont of the
    occurrences of the given term. Currently disqualifying if
    - the term occurs as part of a URL.
    - matches some signatures of known spammy/copy-pasta comments that just list lots of curse words
    - occurs in a subreddit known to have a bad signal-to-noise ratio
    In the future may add more criteria (e.g. if the author appears to be a bot.)
    """
    phrase = term.replace('_', ' ')
    body = comment['body']
    try:
        ix = body.lower().index(phrase)
    except ValueError:
        return False

    # Actually, accept iff match is at the very beginning. Favour precision over recall.
    return ix == 0

    # Accept it if it's near the beginning. "lmao sis not you thinking..."
    if ix < 14:
        return True

    # If not is capitalized, then sure
    if body[ix] == 'N':
        return True

    ctx = body[ix-10:ix]
    return '. ' in ctx or '? ' in ctx

def load_comments(term):
    fname = f'{term}.json'
    path = os.path.join(RAW_DIR, fname)
    with open(path) as f:
        return json.load(f), False

def count_for_term(term, raw):
    comments, sampled = load_comments(term)
    if raw:
        count = len(comments)
    else:
        count = sum(is_valid_comment(c, term) for c in comments)
    if sampled and not raw:
        # Our counts are based on sampling comments from 30 randomly
        # chosen days per year. So scale up by a bit more than a factor
        # of 10
        count *= 365.25 / 30
    return count

def sub_counts_for_term(term, save_json):
    """Return dict mapping subreddit name to count.
    """
    comments, sampled = load_comments(term)
    multiplier = (365.25 / 30) if sampled else 1
    counts = defaultdict(float)
    saved = []
    for comment in comments:
        if not is_valid_comment(comment, term):
            continue
        counts[comment['subreddit']] += multiplier
        if save_json:
            saved.append(comment)
    if save_json:
        out_fname = f'{term}_filtered.json'
        outpath = os.path.join(RAW_DIR, out_fname)
        with open(outpath, 'w') as f:
            json.dump(saved, f, indent=2)
    return counts

def print_per_comment_csv():
    # header
    print("phrase,sub,timestamp,author")
    for phrase in phrase_ids:
        comments, sampled = load_comments(phrase)
        for comment in comments:
            if not is_valid_comment(comment, phrase):
                continue
            row = [phrase, comment['subreddit'], comment['created_utc'], comment['author']]
            print(','.join(map(str, row)))

def print_counts_by_subreddit(save_json):
    # header
    print("phrase,sub,count")
    for phrase in phrase_ids:
        counts = sub_counts_for_term(phrase, save_json)
        for (sub, count) in counts.items():
            print(f"{phrase},{sub},{count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Output a csv of term counts to stdout")
    parser.add_argument('--raw', action='store_true',
            help="Output raw comment counts with no filtering",
    )
    parser.add_argument('--sub', action='store_true',
            help="Add a grouping by subreddit",
    )
    parser.add_argument('--save-json', action='store_true',
            help="Save filtered json",
    )
    parser.add_argument('--timestamps', action='store_true')
    args = parser.parse_args()
    if args.timestamps:
        print_per_comment_csv()
    elif args.sub:
        assert not args.raw, "This combination of args not supported"
        print_counts_by_subreddit(args.save_json)
    else:
        print_all_compound_counts(raw=args.raw)
