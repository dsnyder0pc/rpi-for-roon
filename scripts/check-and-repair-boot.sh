#!/bin/bash

# Proactively checks and cleans the /boot filesystem if needed.
# This script is safe to run at boot (on an unmounted partition)
# or manually on a live system.

LOG_TAG="boot_repair"
BOOT_MOUNT_POINT="/boot"

# Find the device for /boot from /etc/fstab
BOOT_DEVICE=$(grep -E "^\S+\s+$BOOT_MOUNT_POINT\s+" /etc/fstab | awk '{print $1}')

if [ -z "$BOOT_DEVICE" ]; then
    logger -t "$LOG_TAG" "ERROR: Could not find boot device in /etc/fstab."
    exit 1
fi

# --- Manual-Run Safety Check ---
# If run on a live system, /boot must be unmounted first.
was_mounted=0
if mountpoint -q "$BOOT_MOUNT_POINT"; then
    was_mounted=1
    logger -t "$LOG_TAG" "/boot is mounted. Unmounting for check."
    if ! umount "$BOOT_MOUNT_POINT"; then
        logger -t "$LOG_TAG" "ERROR: Failed to unmount $BOOT_MOUNT_POINT. Aborting."
        exit 1
    fi
fi

# --- Conditional Filesystem Check ---
# Check non-destructively first. This is reliable since the partition is unmounted.
if fsck -n "$BOOT_DEVICE" >/dev/null 2>&1; then
    logger -t "$LOG_TAG" "/boot is clean. No action needed."
else
    logger -t "$LOG_TAG" "/boot is not clean. Running repair."
    # A real issue was found, so run the correcting fsck.
    fsck -y "$BOOT_DEVICE"
fi

# --- Remount if it was unmounted by this script ---
if [ "$was_mounted" -eq 1 ]; then
    logger -t "$LOG_TAG" "Remounting /boot."
    mount "$BOOT_MOUNT_POINT"
fi

logger -t "$LOG_TAG" "Check/repair process complete."
exit 0
