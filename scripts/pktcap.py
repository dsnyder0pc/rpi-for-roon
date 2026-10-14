#!/usr/bin/env python3
"""
Record a kernel timestamp for every frame on one interface.

A packet socket with no packages needed, for Pis that carry no tcpdump -- the
Target has no route out in Purist modes, so nothing can be installed there.
Run it on both ends of the Diretta link at once to compare Host send timing
with Target arrival timing.

Timestamps are SO_TIMESTAMPNS, taken by the kernel where the frame meets the
tap, not when this script wakes up, so Python's own scheduling does not leak
into the intervals. On the Host the tap sees outgoing frames (pkttype 4), on
the Target incoming ones (pkttype 0). Only the header is copied; MSG_TRUNC
still reports the full frame length.

The first second after the socket opens is not trustworthy (one interval of
~10 ms was seen there on target2), so analyze_ab.py drops it.

The script pins itself to CPU0, away from the isolated audio cores, but the
tap's per-frame clone still runs where the frame is sent or received. That
cost is identical across A/B arms, not absent.

Output is binary records <q ts_ns><H len><H ethertype><B pkttype>, written
once at the end so the capture does no file I/O while it runs.

Usage (root): pktcap.py IFACE SECONDS OUTFILE
Example:      pktcap.py end0 180 h.bin
"""

import os
import socket
import struct
import sys
import time

SO_TIMESTAMPNS = 35
ETH_P_ALL = 3
REC = struct.Struct('<qHHB')


def main():
    iface, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    os.sched_setaffinity(0, {0})
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8 << 20)
    s.setsockopt(socket.SOL_SOCKET, SO_TIMESTAMPNS, 1)
    s.bind((iface, 0))
    s.settimeout(0.5)
    hdr = bytearray(16)
    buf = bytearray()
    end = time.monotonic() + secs
    while time.monotonic() < end:
        try:
            n, anc, _, addr = s.recvmsg_into([hdr], 64, socket.MSG_TRUNC)
        except socket.timeout:
            continue
        ts = 0
        for lvl, typ, d in anc:
            if lvl == socket.SOL_SOCKET and typ == SO_TIMESTAMPNS:
                sec, ns = struct.unpack('qq', d[:16])
                ts = sec * 1_000_000_000 + ns
        buf += REC.pack(ts, min(n, 65535), (hdr[12] << 8) | hdr[13], addr[2])
    s.close()
    with open(out, 'wb') as f:
        f.write(buf)
    print(f'{len(buf) // REC.size} frames -> {out}')


if __name__ == '__main__':
    main()
