#!/bin/bash

# This script runs on boot to create the Diretta license cache file.

readonly CACHE_FILE="/tmp/diretta_license_url.cache"
readonly TARGET_DIR="/opt/diretta-alsa-target"
readonly LICENSE_APP="${TARGET_DIR}/diretta_app_activate"
readonly LICENSE_URI="https://certificarono.diretta.link/app/"
readonly LOG_TAG="diretta-cache"

# 1. Check if the system is already licensed.
is_licensed=false
if ls "${TARGET_DIR}/" | grep -qv '^diretta'; then
    is_licensed=true
fi

# If it IS licensed, write "Licensed" to the cache and exit.
if [ "$is_licensed" = true ]; then
    echo "Licensed" > "$CACHE_FILE"
    logger -t "$LOG_TAG" "System is already licensed. Skipping activation."
    exit 0
fi

# 2. Wait for the Diretta service to be healthy at the application layer.
timeout=60
check_start_time="$(date +"%s")"

logger -t "$LOG_TAG" "Starting health check for $LICENSE_URI"

until curl -kIfs --connect-timeout 5 "$LICENSE_URI" &>/dev/null; do
    sleep 2
    now="$(date +"%s")"
    elapsed=$((now - check_start_time))
    if [ "$elapsed" -gt "$timeout" ]; then
        logger -t "$LOG_TAG" "Error: Timeout reached ($timeout s) waiting for Diretta server."
        exit 0
    fi
done

# 3. Fetch the license URL and write it to the cache.
if [ -x "$LICENSE_APP" ]; then
    logger -t "$LOG_TAG" "Server is up. Executing $LICENSE_APP"
    license_url=$("$LICENSE_APP")

    # Only write to the cache if we actually got a valid URL back.
    if [[ -n "$license_url" && "$license_url" == http* ]]; then
        echo "$license_url" > "$CACHE_FILE"
        logger -t "$LOG_TAG" "Success: License URL cached."
    else
        logger -t "$LOG_TAG" "Error: Activation app returned invalid response: '$license_url'"
    fi
else
    logger -t "$LOG_TAG" "Error: Activation binary not found or not executable at $LICENSE_APP"
fi

exit 0
