#!/bin/bash
# A/B one key of the Host's /opt/diretta-alsa/setting.inf, measuring the link
# from both ends at once.
#
# Usage: setting-ab.sh OUTDIR KEY VALUE...
#   e.g. setting-ab.sh runs ThredMode 16 18 16 18 16 18
#
# Interleave the values (A B A B ...) so slow drift is not mistaken for an
# effect. Each run restarts diretta_alsa with the value, plays zeros through
# the bridge with aplay, settles, then captures for CAP seconds:
#   Host:   pktcap.py on end0 (send timing), schedsamp (sender thread)
#   Target: pktcap.py on end0 (arrival timing), schedsamp, bufsamp.py (DAC ring)
# A run whose Target DAC is not RUNNING after the settle is logged as FAILED
# and skipped. The original setting.inf is restored at the end. Summarise with
#   analyze_ab.py OUTDIR
#
# HOST and TARGET are ~/.ssh/config aliases; root keys are required on both,
# because the captures need root and sudo cannot prompt from a script. RATE
# must be one aplay plays cleanly into the bridge: aplay underruns at the
# 44.1k family, so the default is 96000.
#
# First used 2026-10-14 for ThredMode 16 vs 18 on an RPi4 pair at 100 Mb/s:
# no measurable difference.
set -u
OUT=$1 KEY=$2; shift 2
HOST=${HOST:-host2} TARGET=${TARGET:-target2}
CAP=${CAP:-180} SETTLE=${SETTLE:-40} RATE=${RATE:-96000}
H=(ssh -o ConnectTimeout=10 "root@$HOST")
T=(ssh -o ConnectTimeout=10 "root@$TARGET")
INF=/opt/diretta-alsa/setting.inf
STATUS=/proc/asound/card0/pcm0p/sub0/status
HERE=$(dirname "$(readlink -f "$0")")
mkdir -p "$OUT"

# Deploy the helpers. The Target has no compiler, so schedsamp is built on the
# Host and relayed through here.
if ! { scp -q "$HERE"/{pktcap.py,schedsamp.c} "root@$HOST:/root/" &&
       "${H[@]}" 'cd /root && gcc -O2 -Wall -o schedsamp schedsamp.c' &&
       scp -q "root@$HOST:/root/schedsamp" "$OUT/.schedsamp" &&
       scp -q "$HERE"/{pktcap.py,bufsamp.py} "$OUT/.schedsamp" "root@$TARGET:/root/" &&
       "${T[@]}" 'mv /root/.schedsamp /root/schedsamp'; }; then
  echo "deploy failed"; exit 1
fi
rm -f "$OUT/.schedsamp"

"${H[@]}" "test -f $INF.pre-ab || cp -p $INF $INF.pre-ab"
i=0
for v in "$@"; do
  i=$((i+1)); R=$(printf '%s/%02d-%s=%s' "$OUT" "$i" "$KEY" "$v"); mkdir -p "$R"
  echo "$(date +%T) run $i $KEY=$v"
  "${H[@]}" "pkill -x aplay; sed -i 's/^$KEY=.*/$KEY=$v/' $INF && systemctl daemon-reload && systemctl restart diretta_alsa && grep ^$KEY= $INF" > "$R/setup.txt" 2>&1
  sleep 8
  # aplay must be detached in its own ssh call: as the tail of a backgrounded
  # && chain it died with the session and the run captured nothing.
  "${H[@]}" "setsid nohup aplay -q -D hw:0,0 -f S32_LE -r $RATE -c 2 -d $((SETTLE+CAP+15)) /dev/zero </dev/null >/root/aplay.log 2>&1 &"
  sleep "$SETTLE"
  if ! "${T[@]}" "grep -q 'state: RUNNING' $STATUS"; then
    echo "$(date +%T) run $i FAILED: Target DAC not RUNNING"; continue
  fi
  "${H[@]}" "ps -eLo tid,cls,rtprio,psr,comm | grep -E 'syncAlsa|end0'" > "$R/host-threads.txt"
  "${H[@]}" "cd /root && rm -f h.bin hs.csv; python3 pktcap.py end0 $CAP h.bin & ./schedsamp -d $CAP -i 2000 -o hs.csv > hs.txt 2>&1 & wait" > "$R/host-cap.txt" 2>&1 &
  "${T[@]}" "cd /root && rm -f t.bin ts.csv tb.csv; python3 pktcap.py end0 $CAP t.bin & python3 bufsamp.py $STATUS $CAP 2000 tb.csv & ./schedsamp -d $CAP -i 2000 -o ts.csv > ts.txt 2>&1 & wait" > "$R/target-cap.txt" 2>&1 &
  wait
  scp -q "root@$HOST":/root/{h.bin,hs.csv,hs.txt,aplay.log} "$R/"
  scp -q "root@$TARGET":/root/{t.bin,ts.csv,ts.txt,tb.csv} "$R/"
  "${H[@]}" "pkill -x aplay; journalctl -u diretta_alsa --since '-5min' --no-pager | tail -20" > "$R/host-journal.txt" 2>&1
  sleep 5
done
"${H[@]}" "mv $INF.pre-ab $INF && systemctl daemon-reload && systemctl restart diretta_alsa && grep ^$KEY= $INF" > "$OUT/restore.txt" 2>&1
echo "$(date +%T) DONE"
touch "$OUT/DONE"
