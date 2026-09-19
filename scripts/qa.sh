#!/bin/bash
#
# Universal QA Launcher for the RPi for Roon Guide
#
# This script detects the hostname and runs the appropriate QA check script.
# It exits non-zero if any check failed, so a caller can gate on it.
#

# Without pipefail a failed download is indistinguishable from a clean run:
# `curl | bash` hands bash an empty script, which exits 0 and would report a
# perfect pass on a machine that was never checked at all. That is the one
# failure this gate must never wave through.
set -o pipefail

# --- Configuration ---
HOST_SCRIPT_URL="https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/diretta-host-checks.sh"
TARGET_SCRIPT_URL="https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/diretta-target-checks.sh"
HOSTNAME=$(hostname)

# --- Main Logic ---
if [[ "$HOSTNAME" == "diretta-target" ]]; then
    echo "Diretta Target detected. Running Target QA checks..."
    curl -fsSL "$TARGET_SCRIPT_URL" | sudo bash
elif [[ "$HOSTNAME" == *diretta* ]]; then
    echo "Diretta Host detected ('${HOSTNAME}'). Running Host QA checks..."
    curl -fsSL "$HOST_SCRIPT_URL" | sudo bash
else
    echo "Error: Could not determine if this is a Diretta Host or Target."
    echo "Please ensure the hostname contains 'diretta' (for a Host) or is 'diretta-target'."
    exit 1
fi
