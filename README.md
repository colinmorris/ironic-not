
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
