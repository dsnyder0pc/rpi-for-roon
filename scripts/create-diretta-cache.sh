#!/bin/bash

# This script runs on boot to create the Diretta license cache file.

readonly CACHE_FILE="/tmp/diretta_license_url.cache"
readonly TARGET_DIR="/opt/diretta-alsa-target"
readonly LICENSE_APP="${TARGET_DIR}/diretta_app_activate"
readonly DIRETTA_SERVER_IP="20.78.113.37"

# 1. Check if the system is already licensed.
is_licensed=false
if ls "${TARGET_DIR}/" | grep -qv '^diretta'; then
    is_licensed=true
fi

# If it IS licensed, write "Licensed" to the cache and exit.
if [ "$is_licensed" = true ]; then
    echo "Licensed" > "$CACHE_FILE"
    exit 0
fi

# If unlicensed, wait for the full network path to be ready by pinging the server.
timeout=30
until ping -c 1 -W 1 "$DIRETTA_SERVER_IP" &>/dev/null; do
    sleep 1
    timeout=$((timeout - 1))
    if [ "$timeout" -eq 0 ]; then
        exit 0
    fi
done

# Fetch the license URL and write it to the cache.
if [ -x "$LICENSE_APP" ]; then
    license_url=$("$LICENSE_APP")

    if [ -n "$license_url" ]; then
        echo "$license_url" > "$CACHE_FILE"
    fi
fi

exit 0
