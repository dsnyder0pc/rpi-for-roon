#!/bin/bash

# Hardened license cache generation utilizing string validation

readonly CACHE_FILE="/tmp/diretta_license_url.cache"
readonly TARGET_DIR="/opt/diretta-alsa-target"
readonly LICENSE_APP="${TARGET_DIR}/diretta_app_activate"
readonly LICENSE_URI="https://certificarono.diretta.link/app/"
readonly LOG_TAG="diretta-cache"

# 1. Verify the activation binary is accessible
if [ ! -x "$LICENSE_APP" ]; then
    logger -t "$LOG_TAG" "Error: Activation binary not found or not executable at $LICENSE_APP"
    exit 0
fi

# 2. Query the binary and capture BOTH stdout and stderr
logger -t "$LOG_TAG" "Querying hardware activation status..."
activation_output=$("$LICENSE_APP" 2>&1)

# 3. If the output is "valid" or completely empty (no errors either), it is licensed.
if [[ "$activation_output" == "valid" || -z "$activation_output" ]]; then
    echo "Licensed" > "$CACHE_FILE"
    logger -t "$LOG_TAG" "Valid local hardware license verified. Skipping activation."
    exit 0
fi

# 4. If we reach here, it either output a URL or threw a curl network error.
# In both cases, the device is trying to reach the internet, meaning it is UNLICENSED.
timeout=75
check_start_time="$(date +"%s")"

logger -t "$LOG_TAG" "Unlicensed hardware or network error detected. Waiting for gateway to reach $LICENSE_URI"

until curl -kIs --connect-timeout 5 "$LICENSE_URI" &>/dev/null; do
    sleep 2
    now="$(date +"%s")"
    elapsed=$((now - check_start_time))
    if [ "$elapsed" -gt "$timeout" ]; then
        logger -t "$LOG_TAG" "Error: Timeout reached ($timeout s) waiting for Diretta server."
        # Cache the last output just in case it was a valid URL
        if [[ "$activation_output" == http* ]]; then
            echo "$activation_output" > "$CACHE_FILE"
        fi
        exit 0
    fi
done

# Gateway is up! Re-run the binary to push the activation handshake and fetch the fresh URL
# This time, we only care about stdout for the URL.
license_url=$("$LICENSE_APP" 2>/dev/null)
if [[ -n "$license_url" && "$license_url" == http* ]]; then
    echo "$license_url" > "$CACHE_FILE"
    logger -t "$LOG_TAG" "Success: Dynamic activation URL cached."
else
    echo "Licensed" > "$CACHE_FILE"
    logger -t "$LOG_TAG" "System successfully processed activation handshake."
fi
