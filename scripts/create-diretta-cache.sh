#!/bin/bash

# This script runs on boot to create the Diretta license cache file.

set -u # Exit if an unset variable is used

readonly CACHE_FILE="/tmp/diretta_license_url.cache"
readonly TARGET_DIR="/opt/diretta-alsa-target"
readonly LICENSE_APP="${TARGET_DIR}/diretta_app_activate"
readonly DIRETTA_SERVER_IP="20.78.113.37"

# 1. Check if the system is already licensed.
is_licensed=false
if ls /opt/diretta-alsa-target/ | grep -qv '^diretta'; then
  is_licensed="true"
fi

if [ "$is_licensed" = true ]; then
    echo "Licensed" > "$CACHE_FILE"
    exit 0
fi

# 2. If unlicensed, wait for a network route to the Diretta server.
# The 'purist-mode-revert-on-boot.service' ensures networking is up.
# We will wait up to 30 seconds for a valid route.
timeout=30
until ip -4 route get "$DIRETTA_SERVER_IP" &>/dev/null; do
    sleep 1
    timeout=$((timeout - 1))
    if [ "$timeout" -eq 0 ]; then
        # If no route appears, exit gracefully. Another attempt will be made on next boot.
        exit 0
    fi
done

# 3. Fetch the license URL and write it to the cache.
if [ -x "$LICENSE_APP" ]; then
    # Capture the output from the application into a variable
    local license_url
    license_url=$("$LICENSE_APP")

    # Only create the cache file if the command actually produced a URL
    if [ -n "$license_url" ]; then
        echo "$license_url" > "$CACHE_FILE"
    fi
    # If the app fails or returns nothing, we simply do nothing.
    # The absence of a cache file is a clearer signal of failure.
fi

exit 0
