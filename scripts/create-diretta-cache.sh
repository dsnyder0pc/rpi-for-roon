#!/bin/bash

# Hardened license cache generation utilizing string validation

readonly CACHE_FILE="/tmp/diretta_license_url.cache"
readonly TARGET_DIR="/opt/diretta-alsa-target"
readonly LICENSE_APP="${TARGET_DIR}/diretta_app_activate"
readonly LOG_TAG="diretta-cache"

# 1. Verify the activation binary is accessible
if [ ! -x "$LICENSE_APP" ]; then
    logger -t "$LOG_TAG" "Error: Activation binary not found or not executable at $LICENSE_APP"
    exit 0
fi

# 2. Loop indefinitely until we receive a definitive response from the hardware activation binary
while true; do
    logger -t "$LOG_TAG" "Querying hardware activation status..."
    activation_output=$("$LICENSE_APP" 2>&1)

    # Case 1: Clean local license affirmation
    if [[ "$activation_output" == "valid" || -z "$activation_output" ]]; then
        echo "Licensed" > "$CACHE_FILE"
        logger -t "$LOG_TAG" "Valid local hardware license verified."
        exit 0
    fi

    # Case 2: Clean registration URL found (Unlicensed state confirmed)
    if [[ "$activation_output" == http* ]]; then
        echo "$activation_output" > "$CACHE_FILE"
        logger -t "$LOG_TAG" "Unlicensed URL verified and cached."
        exit 0
    fi

    # Case 3: Network/Host link error (e.g. "curl_easy_perform() failed:")
    if [[ "$activation_output" == *failed:* || "$activation_output" == *resolve* || "$activation_output" == *connect* ]]; then
        logger -t "$LOG_TAG" "Network path unavailable. Retrying initialization..."
        sleep 2
    else
        # Safe catch-all fallback for unexpected application errors
        echo "Restart Target to Connect to Diretta License Server" > "$CACHE_FILE"
        logger -t "$LOG_TAG" "Unexpected output encountered: $activation_output"
        exit 1
    fi
done
