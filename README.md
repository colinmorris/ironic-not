Some hacky code for scraping and analyzing Reddit comments that use 'ironic *not*'. Examples:

> Not them trying to pretend that Michelle's screaming at the girls for real.

> Not me using my migraine today as an excuse to buy another squishmallow!!!!

> STOP! Omg not the Dream Flowey bahahaha.

> LMAO not Scott Pilgrim

Discussed in [this blog post](http://colinmorris.github.io/blog/ironic-not).

## Pattern matching

The patterns to search for are defined in `phrases.py`. The main patterns have the form "Not `pronoun` `verbing`".

However, not all uses of this construction involve a gerund-participial clause (see the third and fourth examples above). To attempt to catch some of these, we also search for the patterns "lmao not" and "omg not". These have a high false positive rate (even after the filtering step described below), so I excluded them from my quantitative analyses (in the included ipython notebooks), and only used them as a source from which to manually curate examples.

## Data files

- `sub_counts.csv` gives the number of matching comments per subreddit in descending order (not including non-gerund patterns)
- `comments.csv` has a row per comment, with columns for timestamp, author, subreddit, and which pattern the comment matched
- `counts.csv` is like the above but aggregated per subreddit and pattern

## Pipeline

### 1. Scrape reddit comments

```
python reddit_counts.py
```

This will download all Reddit comments matching the patterns in `phrases.py` to json files in `comment_data/`. They will go to one file per phrase (e.g. `not_me_thinking.json`).

You can modify the global variables at the top of the file to tweak the parameters of the scrape, particularly `END_TIMESTAMP` and `EARLIEST_TIMESTAMP` to change the date range of comments downloaded.

### 2. Filter and aggregate

```
python compute_counts.py --sub --save-json > counts.csv
```

This will apply some filtering specified in the function `is_valid_comment()` in `compute_counts.py` to attempt to remove false positive matches. The most salient feature is generally the matching "Not..." phrase appearing very near the beginning of the comment. These filters will typically reduce the raw comment volume by around 50-80%. The comments that make it through the filter will be saved in new json files - e.g. `not_me_thinking_filtered.json`.

This will also leave us with a csv file, `counts.csv`, with columns for phrase, subreddit, and count.

For the purposes of some other analyses you can also generate a csv with a row per comment by running:

```
python compute_counts.py --timestamps > comments.csv
```
