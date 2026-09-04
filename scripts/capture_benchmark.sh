#!/bin/bash

# --- Configuration (Automated) ---

# 1. Identify Local Diretta Interface (Host end0)
# We assume 'end0' is always the P2P link.
if [ -f "/sys/class/net/end0/address" ]; then
    HOST_MAC_1=$(cat /sys/class/net/end0/address)
else
    echo "Error: interface 'end0' not found."
    exit 1
fi

# 2. Identify Local Uplink Interface (Host Roon/Internet)
# We find the interface holding the default route.
UPLINK_IF=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -n "$UPLINK_IF" ]; then
    # SC2086 Fix: Quote the variable inside the path
    HOST_MAC_2=$(cat /sys/class/net/"$UPLINK_IF"/address)
else
    echo "Error: No default uplink found."
    exit 1
fi

# 3. Identify Target MAC (Target end0)
# We use the hostname 'diretta-target' which we validated in the QA checks.
TARGET_IP="diretta-target"

# Force a ping to ensure arp table is warm
ping -c 1 -W 1 "$TARGET_IP" >/dev/null 2>&1

# Get the MAC address for the resolved IP
# We fetch the IP via getent, then grep the neighbor table
TARGET_RESOLVED=$(getent hosts "$TARGET_IP" | awk '{print $1}')
TARGET_MAC=$(ip neigh show | grep "$TARGET_RESOLVED" | awk '{print $5}' | head -n1)

# Fallback/Debug Output
echo "--- Detected Configuration ---"
echo "Host Diretta (end0):   $HOST_MAC_1"
echo "Host Uplink ($UPLINK_IF): $HOST_MAC_2"
echo "Target MAC:            $TARGET_MAC"
echo "------------------------------"

CAPTURE_INTERFACE="end0"
CAPTURE_DURATION=180          # 3 Minutes
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_PCAP="diretta_bench_${TIMESTAMP}.pcap"
OUTPUT_CSV="diretta_bench_${TIMESTAMP}.csv"
# --- End Configuration ---

until sudo id; do
  echo "try again"
done

# Verify dependencies (Audiolinux/Arch and Debian/Ubuntu support)
for cmd in tcpdump tshark; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Installing $cmd..."
        if command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm --needed wireshark-cli tcpdump
        elif command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y tshark tcpdump
        else
            echo "Error: package manager not supported. Please install $cmd manually."
            exit 1
        fi
    fi
done

# Prefer nanosecond timestamps. At the default microsecond resolution the
# inter-packet intervals quantize to whole microseconds, which floors the
# jitter statistics: once most intervals land in one 1us bin the IQR reads
# 0.00us by construction rather than because the stream is perfect.
# Not every tcpdump build offers the option, so probe before relying on it.
if tcpdump -h 2>&1 | grep -q -- '--time-stamp-precision'; then
    TSTAMP_OPT="--time-stamp-precision=nano"
    echo "✓ Nanosecond timestamps enabled."
else
    TSTAMP_OPT=""
    echo "⚠ tcpdump lacks --time-stamp-precision; falling back to microseconds."
    echo "  Jitter (IQR) may read 0.00us because of timestamp quantization."
fi

echo "▶️  Starting ${CAPTURE_DURATION}-second Benchmark Capture on ${CAPTURE_INTERFACE}..."
echo "    (Capturing ALL traffic headers to analyze noise)"

# Capture command:
# -s 128: Snaplen 128 bytes (Headers only, saves space)
# not port 22: Exclude your SSH session from the "Noise" analysis
# SC2086 Fix: Quoted all variables
# SC2086: $TSTAMP_OPT is intentionally unquoted so an empty value expands away.
# shellcheck disable=SC2086
timeout "${CAPTURE_DURATION}" sudo tcpdump -i "${CAPTURE_INTERFACE}" -s 128 ${TSTAMP_OPT} -w "${OUTPUT_PCAP}" -n 'not port 22' &

PID=$!
echo "    Capture running (PID $PID). Waiting ${CAPTURE_DURATION}s..."
wait "$PID"

echo "✅ Capture complete: ${OUTPUT_PCAP}"
echo "⚙️  Exporting data for Python analysis..."

# Tshark export:
# We extract specific fields to identify Audio vs. Noise
# eth.type: To distinguish IPv4/IPv6/ARP/Diretta
# ip.proto: To distinguish TCP/UDP/ICMP
# occurrence=f: Emit only the first value per field. Without it, packets that
#   repeat a field (an ICMP error quoting an inner IP header) export an escaped
#   comma inside the field and break the CSV column count.
# SC2086 Fix: Quoted input and output filenames
tshark -r "${OUTPUT_PCAP}" \
    -T fields \
    -E header=y -E separator=, -E occurrence=f \
    -e frame.time_relative \
    -e frame.len \
    -e eth.src \
    -e eth.dst \
    -e eth.type \
    -e ip.proto \
    > "${OUTPUT_CSV}"

echo "✅ Analysis Data Ready: ${OUTPUT_CSV}"
