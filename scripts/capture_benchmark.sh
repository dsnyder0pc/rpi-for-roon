#!/bin/bash

# --- Configuration ---
# MACs identified from your 'ip link show'
HOST_MAC_1="2c:cf:67:7a:7e:26" # end0 on 'diretta-office'
HOST_MAC_2="8c:ae:4c:cd:a3:b8" # enp1s0u1u4 on 'diretta-office'
TARGET_MAC="2c:cf:67:c5:b4:36" # end0 on 'diretta-target'

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
timeout ${CAPTURE_DURATION} sudo tcpdump -i ${CAPTURE_INTERFACE} -s 128 -w ${OUTPUT_PCAP} -n 'not port 22' &

PID=$!
echo "    Capture running (PID $PID). Waiting ${CAPTURE_DURATION}s..."
wait $PID

echo "✅ Capture complete: ${OUTPUT_PCAP}"
echo "⚙️  Exporting data for Python analysis..."

# Tshark export:
# We extract specific fields to identify Audio vs. Noise
# eth.type: To distinguish IPv4/IPv6/ARP/Diretta
# ip.proto: To distinguish TCP/UDP/ICMP
tshark -r ${OUTPUT_PCAP} \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    -e eth.src \
    -e eth.dst \
    -e eth.type \
    -e ip.proto \
    > ${OUTPUT_CSV}

echo "✅ Analysis Data Ready: ${OUTPUT_CSV}"
