#!/bin/bash

# --- CONFIGURATION ---
# 1. The Interface facing your Home Network (Input/RAAT)
#    (Check 'ip addr', likely enp1s0u2 or similar)
IFACE_LAN="enp1s0u2"

# 2. The IP Address of your Roon Core
#    (Crucial for isolating the RAAT stream from other LAN noise)
ROON_CORE_IP="172.16.8.8"

# 3. The Interface facing the Diretta Target (Output/DDS)
#    (Likely end0 on a Pi 4)
IFACE_TARGET="end0"

# 4. Duration of capture in seconds
DURATION=60

# ---------------------

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILE_RAAT="raat_input_${TIMESTAMP}"
FILE_DIRETTA="diretta_output_${TIMESTAMP}"

echo "======================================================="
echo "   Diretta Host: Input vs. Output Traffic Capture"
echo "======================================================="
echo "Configured Roon Core IP: ${ROON_CORE_IP}"
echo "Capture Duration:        ${DURATION} seconds"
echo "-------------------------------------------------------"

# 1. Check for sudo
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (sudo)"
  exit
fi

# 2. Start RAAT Capture (Background)
#    Filters for traffic TO/FROM the Roon Core only.
echo "▶️  Starting RAAT Capture on ${IFACE_LAN}..."
tcpdump -i ${IFACE_LAN} -n host ${ROON_CORE_IP} -w ${FILE_RAAT}.pcap &
PID_RAAT=$!

# 3. Start Diretta Capture (Background)
#    Captures everything on the point-to-point link (except SSH).
echo "▶️  Starting Diretta Capture on ${IFACE_TARGET}..."
tcpdump -i ${IFACE_TARGET} -n not port 22 -w ${FILE_DIRETTA}.pcap &
PID_DIRETTA=$!

echo "⏳ Capturing data... Start music in Roon NOW!"
sleep ${DURATION}

# 4. Stop Captures
echo "🛑 Stopping captures..."
kill $PID_RAAT
kill $PID_DIRETTA
wait $PID_RAAT 2>/dev/null
wait $PID_DIRETTA 2>/dev/null

echo "✅ PCAP files saved."
echo "-------------------------------------------------------"
echo "⚙️  Processing to CSV for analysis..."

# 5. Convert RAAT PCAP to CSV
#    We need Time and Length. 
tshark -r ${FILE_RAAT}.pcap \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    > ${FILE_RAAT}.csv
echo "   -> ${FILE_RAAT}.csv created."

# 6. Convert Diretta PCAP to CSV
tshark -r ${FILE_DIRETTA}.pcap \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    > ${FILE_DIRETTA}.csv
echo "   -> ${FILE_DIRETTA}.csv created."

echo "======================================================="
echo "DONE. Please upload the two .csv files to the chat."
