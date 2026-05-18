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

# 2. Query the binary directly to evaluate the exact license string
logger -t "$LOG_TAG" "Querying hardware activation status..."
activation_output=$("$LICENSE_APP")

# If the output is "valid" or completely empty, the board is licensed locally (no WAN required)
if [[ "$activation_output" == "valid" || -z "$activation_output" ]]; then
    echo "Licensed" > "$CACHE_FILE"
    logger -t "$LOG_TAG" "Valid local hardware license verified. Skipping activation."
    exit 0
fi

# 3. If we got an HTTP registration link, the hardware is unlicensed or swapped
if [[ "$activation_output" == http* ]]; then
    timeout=150
    check_start_time="$(date +"%s")"

    logger -t "$LOG_TAG" "Unlicensed/Swapped hardware detected. Waiting for gateway to reach $LICENSE_URI"

    until curl -kIs --connect-timeout 5 "$LICENSE_URI" &>/dev/null; do
        sleep 2
        now="$(date +"%s")"
        elapsed=$((now - check_start_time))
        if [ "$elapsed" -gt "$timeout" ]; then
            logger -t "$LOG_TAG" "Error: Timeout reached ($timeout s) waiting for Diretta server."
            # Cache the URL anyway so the Host Web UI can display the registration QR code offline
            echo "$activation_output" > "$CACHE_FILE"
            exit 0
        fi
    done

    # Gateway is up! Re-run the binary to push the activation handshake and fetch the fresh URL
    license_url=$("$LICENSE_APP")
    if [[ -n "$license_url" && "$license_url" == http* ]]; then
        echo "$license_url" > "$CACHE_FILE"
        logger -t "$LOG_TAG" "Success: Dynamic activation URL cached."
    else
        echo "Licensed" > "$CACHE_FILE"
        logger -t "$LOG_TAG" "System successfully processed activation handshake."
    fi
else
    # Fallback catch-all for unexpected binary responses
    echo "Licensed" > "$CACHE_FILE"
    logger -t "$LOG_TAG" "Assuming licensed state based on response: $activation_output"
fi

exit 0
