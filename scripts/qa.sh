#!/bin/bash
#
# Universal QA Launcher for the RPi for Roon Guide
#
# This script detects the hostname and runs the appropriate QA check script.
#

# --- Configuration ---
HOST_SCRIPT_URL="https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/diretta-host-checks.sh"
TARGET_SCRIPT_URL="https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/diretta-target-checks.sh"
HOSTNAME=$(hostname)

# --- Main Logic ---
if [[ "$HOSTNAME" == "diretta-host" ]]; then
    echo "Diretta Host detected. Running Host QA checks..."
    curl -fsSL "$HOST_SCRIPT_URL" | sudo bash
elif [[ "$HOSTNAME" == "diretta-target" ]]; then
    echo "Diretta Target detected. Running Target QA checks..."
    curl -fsSL "$TARGET_SCRIPT_URL" | sudo bash
else
    echo "Error: Could not determine if this is a Diretta Host or Target."
    echo "Please ensure the hostname is set to 'diretta-host' or 'diretta-target'."
    exit 1
fi
