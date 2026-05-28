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

logger -t "$LOG_TAG" "Unlicensed hardware or network error detected. Waiting for gateway to reach $LICENSE_URI"

# Protect licensed machines that might fall through due to curl failures when completely offline
timeout=30
check_start_time="$(date +"%s")"
while true; do
    curl -kIs --connect-timeout 5 "$LICENSE_URI" &>/dev/null
    curl_status=$?

    # 0 means pure success, we are done
    if [[ $curl_status -eq 0 ]]; then
        break
    fi

    # Check for timeout to ensure we don't loop forever when offline or when Purist Mode is activated
    now="$(date +"%s")"
    elapsed=$((now - check_start_time))
    if [[ $elapsed -gt $timeout ]]; then
        logger -t "$LOG_TAG" "Timeout reached ($timeout s) waiting for gateway."
        # If the original activation output was a registration URL, cache it
        if [[ "$activation_output" == http* ]]; then
            echo "$activation_output" > "$CACHE_FILE"
            logger -t "$LOG_TAG" "Unlicensed URL cached after timeout."
        else
            # Otherwise, it was a curl error on a licensed machine, so cache "Licensed"
            echo "Licensed" > "$CACHE_FILE"
            logger -t "$LOG_TAG" "Assuming Licensed state after timeout."
        fi
        exit 0
    fi

    # Only retry if the error points to a local routing/DNS delay on the Host
    if [[ $curl_status -eq 6 || $curl_status -eq 7 || $curl_status -eq 28 || $curl_status -eq 97 ]]; then
        sleep 2
    else
        logger -t "$LOG_TAG" "Curl failed with permanent exit code $curl_status. Breaking loop."
        echo "Restart Target to Connect to Diretta License Server" > "$CACHE_FILE"
        exit 1
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
