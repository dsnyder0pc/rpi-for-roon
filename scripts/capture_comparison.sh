#!/bin/bash

# --- CONFIGURATION (Automated) ---

# 1. Identify Diretta Interface (Output/Target)
#    We assume 'end0' is always the P2P link.
if [ -d "/sys/class/net/end0" ]; then
    IFACE_TARGET="end0"
else
    echo "❌ Error: Diretta interface 'end0' not found."
    exit 1
fi

# 2. Identify LAN Interface (Input/RAAT)
#    We find the interface holding the default route to the internet/LAN.
IFACE_LAN=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -z "$IFACE_LAN" ]; then
    echo "❌ Error: No default uplink found for LAN traffic."
    exit 1
fi

# 3. Roon Core IP
#    (Keep this matched to your setup, but we check reachability below)
ROON_CORE_IP="172.16.8.8"

# 4. Duration
DURATION=60

# --- Validation ---
echo "--- Configuration Detected ---"
echo " LAN Interface:    ${IFACE_LAN} (RAAT Input)"
echo " Target Interface: ${IFACE_TARGET} (Diretta Output)"
echo " Roon Core IP:     ${ROON_CORE_IP}"
echo "------------------------------"

# Verify Roon Core is reachable
if ! ping -c 1 -W 1 "${ROON_CORE_IP}" &> /dev/null; then
    echo "⚠️  WARNING: Roon Core (${ROON_CORE_IP}) is not reachable!"
    echo "    Check the IP in the script or ensure Roon is on."
    echo "    (Press Ctrl+C to abort, or wait 5s to proceed anyway)"
    sleep 5
fi

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

# Start RAAT Capture (Background)
# Filters for traffic TO/FROM the Roon Core only.
echo "▶️  Starting RAAT Capture on ${IFACE_LAN}..."
timeout "${DURATION}" sudo tcpdump -i "${IFACE_LAN}" -n host "${ROON_CORE_IP}" -w "${FILE_RAAT}.pcap" &
PID_RAAT=$!

# Start Diretta Capture (Background)
# Captures everything on the point-to-point link (except SSH).
echo "▶️  Starting Diretta Capture on ${IFACE_TARGET}..."
timeout "${DURATION}" sudo tcpdump -i "${IFACE_TARGET}" -n not port 22 -w "${FILE_DIRETTA}.pcap" &
PID_DIRETTA=$!

echo "⏳ Capturing data... Start music in Roon NOW!"
wait "${PID_RAAT}" "${PID_DIRETTA}" 2>/dev/null

echo "✅ PCAP files saved."
echo "-------------------------------------------------------"
echo "⚙️  Processing to CSV for analysis..."

# Ensure files are readable by the current user
sudo chmod 644 "${FILE_RAAT}.pcap" "${FILE_DIRETTA}.pcap" 2>/dev/null || true

# Convert RAAT PCAP to CSV
tshark -r "${FILE_RAAT}.pcap" \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    > "${FILE_RAAT}.csv"
echo "   -> ${FILE_RAAT}.csv created."

# Convert Diretta PCAP to CSV
tshark -r "${FILE_DIRETTA}.pcap" \
    -T fields \
    -E header=y -E separator=, \
    -e frame.time_relative \
    -e frame.len \
    > "${FILE_DIRETTA}.csv"
echo "   -> ${FILE_DIRETTA}.csv created."

echo "======================================================="
echo "DONE. Please run analyze_comparison.py on the CSV files:"
echo "python3 scripts/analyze_comparison.py ${FILE_RAAT}.csv ${FILE_DIRETTA}.csv"
