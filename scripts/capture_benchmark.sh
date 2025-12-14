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

# Ensure tools are installed
if ! command -v tshark &> /dev/null; then
    echo "Installing wireshark-cli..."
    sudo pacman -S --noconfirm --needed wireshark-cli
fi
if ! command -v tcpdump &> /dev/null; then
    echo "Installing tcpdump..."
    sudo pacman -S --noconfirm --needed tcpdump
fi

echo "▶️  Starting ${CAPTURE_DURATION}-second Benchmark Capture on ${CAPTURE_INTERFACE}..."
echo "    (Capturing ALL traffic headers to analyze noise)"

# Capture command:
# -s 128: Snaplen 128 bytes (Headers only, saves space)
# not port 22: Exclude your SSH session from the "Noise" analysis
# SC2086 Fix: Quoted all variables
timeout "${CAPTURE_DURATION}" sudo tcpdump -i "${CAPTURE_INTERFACE}" -s 128 -w "${OUTPUT_PCAP}" -n 'not port 22' &

PID=$!
echo "    Capture running (PID $PID). Waiting ${CAPTURE_DURATION}s..."
wait "$PID"

echo "✅ Capture complete: ${OUTPUT_PCAP}"
echo "⚙️  Exporting data for Python analysis..."

# Tshark export:
# We extract specific fields to identify Audio vs. Noise
# eth.type: To distinguish IPv4/IPv6/ARP/Diretta
# ip.proto: To distinguish TCP/UDP/ICMP
# SC2086 Fix: Quoted input and output filenames
tshark -r "${OUTPUT_PCAP}" \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    -e eth.src \
    -e eth.dst \
    -e eth.type \
    -e ip.proto \
    > "${OUTPUT_CSV}"

echo "✅ Analysis Data Ready: ${OUTPUT_CSV}"
