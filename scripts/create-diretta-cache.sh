#!/bin/bash

# Hardened license cache generation utilizing string validation
#
# The cache lives under /run rather than /tmp on purpose. The Target has no
# battery-backed clock, so it boots with a stale date and chronyd steps the
# clock forward once the Host is reachable. A file written to /tmp before that
# step looks months old afterwards, and systemd-tmpfiles-clean.timer deletes
# anything in /tmp older than 10 days. /run is tmpfs, is cleared on every boot,
# and is never touched by systemd-tmpfiles-clean.

readonly CACHE_DIR="/run/diretta"
readonly CACHE_FILE="${CACHE_DIR}/license.cache"
readonly TARGET_DIR="/opt/diretta-alsa-target"
readonly LICENSE_APP="${TARGET_DIR}/diretta_app_activate"
readonly LOG_TAG="diretta-cache"
readonly RETRY_DELAY=2
readonly MAX_ATTEMPTS=150  # ~5 minutes of retries before giving up

# Write the cache atomically so the Purist Mode web app never reads a partial file
write_cache() {
    local content="$1"
    local tmp

    mkdir -p "$CACHE_DIR"
    tmp=$(mktemp "${CACHE_FILE}.XXXXXX") || {
        logger -t "$LOG_TAG" "Error: Unable to create a temporary file in $CACHE_DIR"
        return 1
    }

    printf '%s\n' "$content" > "$tmp"
    chmod 0644 "$tmp"
    mv -f "$tmp" "$CACHE_FILE"
}

# 1. Verify the activation binary is accessible
if [ ! -x "$LICENSE_APP" ]; then
    logger -t "$LOG_TAG" "Error: Activation binary not found or not executable at $LICENSE_APP"
    exit 0
fi

# 2. Loop until we receive a definitive response from the hardware activation binary
attempt=0
while (( attempt < MAX_ATTEMPTS )); do
    (( attempt++ ))
    logger -t "$LOG_TAG" "Querying hardware activation status (attempt ${attempt}/${MAX_ATTEMPTS})..."
    activation_output=$("$LICENSE_APP" 2>&1)

    # Case 1: Clean local license affirmation
    if [[ "$activation_output" == "valid" || -z "$activation_output" ]]; then
        write_cache "Licensed"
        logger -t "$LOG_TAG" "Valid local hardware license verified."
        exit 0
    fi

    # Case 2: Clean registration URL found (Unlicensed state confirmed)
    if [[ "$activation_output" == http* ]]; then
        write_cache "$activation_output"
        logger -t "$LOG_TAG" "Unlicensed URL verified and cached."
        exit 0
    fi

    # Case 3: Network/Host link error (e.g. "curl_easy_perform() failed:")
    if [[ "$activation_output" == *failed:* || "$activation_output" == *resolve* || "$activation_output" == *connect* ]]; then
        logger -t "$LOG_TAG" "Network path unavailable. Retrying initialization..."
        sleep "$RETRY_DELAY"
    else
        # Safe catch-all fallback for unexpected application errors. Exit 0 so a
        # transient application error does not leave the unit in a failed state
        # and block purist-mode-auto.service, which is ordered After= this one.
        write_cache "Restart Target to Connect to Diretta License Server"
        logger -t "$LOG_TAG" "Unexpected output encountered: $activation_output"
        exit 0
    fi
done

# 3. Retries exhausted. Leave a readable message rather than an empty cache.
write_cache "Restart Target to Connect to Diretta License Server"
logger -t "$LOG_TAG" "Gave up after ${MAX_ATTEMPTS} attempts. Wrote fallback message to $CACHE_FILE"
exit 0
