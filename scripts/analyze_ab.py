#!/usr/bin/env python3
"""
Summarise a setting-ab.sh output directory, one column per run, then the
mean per value.

Rows:
  h_*   Host send intervals (us), from the Host's pktcap.py capture
  t_*   Target arrival intervals (us), from the Target's capture
        sd, iqr, p1-99, p.1-99.9 spreads; max; roll = peak-to-peak of the
        100-cycle rolling mean (slow wander rather than per-frame jitter)
  buf_* Target DAC ring: sd of delay, and the lowest appl_ptr - hw_ptr fill
  snd_* Host sender thread (the SCHED_RR syncAlsa on CPU2) per wakeup, from
        schedsamp's cumulative counters

Audio frames are the dominant ethertype in the capture (0xcb4b, raw L2) at
close to the modal size; IPv6 InfoCycle reports and other traffic drop out.
The first second of each capture is discarded, because the packet socket's
first interval is unreliable.

Usage: analyze_ab.py OUTDIR
"""

import glob
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

REC = np.dtype([('ts', '<i8'), ('len', '<u2'), ('et', '<u2'), ('pt', 'u1')])
PKT_OUTGOING, PKT_HOST = 4, 0


def audio_frames(path, pkttype):
    a = np.fromfile(path, dtype=REC)
    a = a[a['pt'] == pkttype]
    et = Counter(a['et'].tolist()).most_common(1)[0][0]
    a = a[a['et'] == et]
    size = Counter(a['len'].tolist()).most_common(1)[0][0]
    a = a[a['len'] >= size * 0.9]
    return a[a['ts'] > a['ts'][0] + 1_000_000_000]


def interval_stats(a, prefix):
    d = np.diff(a['ts']) / 1000.0
    p = np.percentile(d, [0.1, 1, 25, 75, 99, 99.9])
    roll = np.convolve(d, np.ones(100) / 100, 'valid')
    return {f'{prefix}_sd': d.std(), f'{prefix}_iqr': p[3] - p[2],
            f'{prefix}_p1-99': p[4] - p[1], f'{prefix}_p.1-99.9': p[5] - p[0],
            f'{prefix}_max': d.max(), f'{prefix}_roll': roll.max() - roll.min()}


def buffer_stats(path):
    b = pd.read_csv(path)
    run = b[b.state == 'RUNNING']
    fill = run.appl_ptr.astype(int) - run.hw_ptr.astype(int)
    return {'buf_delay_sd': run.delay.astype(float).std(), 'buf_fill_min': fill.min(),
            'buf_fill_mean': fill.mean(), 'xrun': int((b.state == 'XRUN').sum())}


def sender_stats(run_dir):
    tid = next(l.split()[0] for l in open(f'{run_dir}/host-threads.txt')
               if l.split()[1] == 'RR' and l.split()[3] == '2')
    hs = pd.read_csv(f'{run_dir}/hs.csv')
    delta = {k: hs[f'syncAlsa_{tid}_{k}'].iloc[-1] - hs[f'syncAlsa_{tid}_{k}'].iloc[0]
             for k in ('run', 'wait', 'slices')}
    secs = (hs.t_ns.iloc[-1] - hs.t_ns.iloc[0]) / 1e9
    return {'snd_run_us': delta['run'] / delta['slices'] / 1e3,
            'snd_wait_us': delta['wait'] / delta['slices'] / 1e3,
            'snd_wakes_s': delta['slices'] / secs}


def main():
    rows = []
    for d in sorted(glob.glob(os.path.join(sys.argv[1], '[0-9][0-9]-*'))):
        if not os.path.exists(f'{d}/h.bin'):
            continue  # a FAILED run
        num, _, kv = os.path.basename(d).partition('-')
        r = {'run': num, 'value': kv.partition('=')[2]}
        r.update(interval_stats(audio_frames(f'{d}/h.bin', PKT_OUTGOING), 'h'))
        r.update(interval_stats(audio_frames(f'{d}/t.bin', PKT_HOST), 't'))
        r.update(buffer_stats(f'{d}/tb.csv'))
        r.update(sender_stats(d))
        rows.append(r)
    df = pd.DataFrame(rows).set_index('run')
    pd.set_option('display.width', 250)
    pd.set_option('display.precision', 2)
    print(df.T.to_string())
    print('\nmean by value:')
    print(df.groupby('value').mean(numeric_only=True).T.to_string())


if __name__ == '__main__':
    main()
