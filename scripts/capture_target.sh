#!/bin/bash

# --- Target Configuration ---
CAPTURE_INTERFACE="end0"
CAPTURE_DURATION=60           # 60 seconds is plenty to catch seven or eight 8s cycles
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_PCAP="target_noise_${TIMESTAMP}.pcap"
OUTPUT_CSV="target_noise_${TIMESTAMP}.csv"

echo "--- Target Environment ---"
if [ -f "/sys/class/net/${CAPTURE_INTERFACE}/address" ]; then
    TARGET_MAC=$(cat /sys/class/net/${CAPTURE_INTERFACE}/address)
    echo "Target Interface: ${CAPTURE_INTERFACE} ($TARGET_MAC)"
else
    echo "Error: Interface ${CAPTURE_INTERFACE} not found."
    exit 1
fi
echo "--------------------------"

# Ensure root privileges safely
until sudo id; do
  echo "Privilege escalation required. Please try again."
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

echo "▶️  Starting ${CAPTURE_DURATION}s header capture on ${CAPTURE_INTERFACE}..."
echo "    (Filtering out SSH to isolate background traffic)"

# Capture headers only, ignoring your active SSH terminal
timeout "${CAPTURE_DURATION}" sudo tcpdump -i "${CAPTURE_INTERFACE}" -s 128 -w "${OUTPUT_PCAP}" -n 'not port 22' &

PID=$!
wait "$PID"

echo "✅ Capture complete: ${OUTPUT_PCAP}"
echo "⚙️  Extracting Layer 2 / Layer 3 telemetry..."

# Exporting relative time, packet size, MACs, EtherType, and IP Protocol
tshark -r "${OUTPUT_PCAP}" \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    -e eth.src \
    -e eth.dst \
    -e eth.type \
    -e ip.proto \
    -e ipv6.nxt \
    > "${OUTPUT_CSV}"

echo "✅ Target Data Ready: ${OUTPUT_CSV}"

echo "📊 Quick Summary of Non-Audio EtherTypes found:"
tail -n +2 "${OUTPUT_CSV}" | awk -F, '{print $5}' | sort | uniq -c
