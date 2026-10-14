#!/usr/bin/env python3
"""
Sample an ALSA playback substream's buffer state at a fixed interval.

On a Target this shows how Diretta manages the DAC buffer: how full it keeps
the ring, how low it ever gets, and whether the level drifts. The status file
is world-readable, so no root is needed.

Useful columns:
  appl_ptr - hw_ptr   frames written but not yet taken by the hardware, i.e.
                      the ring's fill. Compare with buffer_size in hw_params.
  delay               fill plus what sits beyond the ring (USB, DAC FIFO).
  state               RUNNING, or XRUN when the ring ran dry.

Measured on target2 (AlsaLatency=30, 96 kHz): a 2880-frame ring of 4 x 720
held ~94% full, never below ~77%, with ~920 more frames past it in USB/DAC.

The sampler pins itself to CPU0. Rows are kept in memory and written at the
end. Reading /proc text costs far more than the Python around it, so 2 ms is
a comfortable interval.

Usage: bufsamp.py STATUSFILE SECONDS INTERVAL_US OUTFILE
Example: bufsamp.py /proc/asound/card0/pcm0p/sub0/status 180 2000 tb.csv
"""

import os
import sys
import time

KEYS = ('delay', 'avail', 'avail_max', 'hw_ptr', 'appl_ptr')


def main():
    path, secs, iv, out = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    os.sched_setaffinity(0, {0})
    rows = []
    fd = os.open(path, os.O_RDONLY)
    nxt = time.monotonic_ns()
    end = nxt + int(secs * 1e9)
    while nxt < end:
        os.lseek(fd, 0, os.SEEK_SET)
        txt = os.read(fd, 4096).decode()
        t = time.monotonic_ns()
        f = {}
        for line in txt.splitlines():
            k, _, v = line.partition(':')
            f[k.strip()] = v.strip()
        rows.append((t, f.get('state', 'closed'), *(f.get(k, '') for k in KEYS)))
        nxt += iv * 1000
        d = nxt - time.monotonic_ns()
        if d > 0:
            time.sleep(d / 1e9)
    os.close(fd)
    with open(out, 'w') as fh:
        fh.write('t_ns,state,' + ','.join(KEYS) + '\n')
        for r in rows:
            fh.write(','.join(map(str, r)) + '\n')
    print(f'{len(rows)} samples -> {out}')


if __name__ == '__main__':
    main()
