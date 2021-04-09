import os

OUT_DIR = '../supercut/clips'

def int_if_possible(numstr):
    try:
        return int(numstr)
    except ValueError:
        return float(numstr)

def parse_timestamp_s(ts_str):
    parts = ts_str.split(':')
    assert len(parts) == 3
    hrs, mins, secs = map(int_if_possible, parts)
    return hrs*(60*60) + mins*60 + secs

def make_command(ix, fname, startstr, endstr):
    starts = parse_timestamp_s(startstr)
    ends = parse_timestamp_s(endstr)
    delta = ends - starts
    assert delta > 0
    out_fname = f'{ix}_{fname[:fname.index(".")]}.mp4'
    outpath = os.path.join(OUT_DIR, out_fname)
    #return f'ffmpeg -y -ss {starts} -i {fname} -c copy -t {delta} {outpath}'
    SSTRICK = 1
    if SSTRICK:
        # Trick to supposedly speed things up: https://superuser.com/a/704118
        # (Does seem to be a bit faster? But hard to say.)
        wiggle = 40
        assert starts > wiggle
        return f'ffmpeg -y -ss {starts-wiggle} -i {fname} -ss {wiggle} -t {delta} {outpath}'
    return f'ffmpeg -y -ss {starts} -i {fname} -t {delta} {outpath}'

f = open('clips.tsv')
i = 0
for i, line in enumerate(f):
    parts = line.split('\t')
    if len(parts) != 3:
        cmd = f'# Skipping {line.strip()}'
    else:
        cmd = make_command(i, *parts)
        i += 1
    print(cmd)
