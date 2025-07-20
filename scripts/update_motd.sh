#!/bin/bash
#
# This script updates the MOTD with the primary IP address (IPv4 preferred)
# by checking which source IP the kernel uses for the default route.
# This correctly handles interfaces with multiple IP aliases.
#

MOTD_FILE="/etc/motd"
IP_ADDR=""

# First, remove any old IP address lines from the motd
sed -i '/^Your IP address is/d' "$MOTD_FILE"

# --- Try to find the primary IPv4 address ---
# We ask the kernel for the route to a public IP (Cloudflare).
# The 'src' field in the output is the primary IP it would use.
IP_ADDR=$(ip -4 route get 1.1.1.1 2>/dev/null | grep -oP 'src \K[\d.]+')

# --- If no IPv4 address was found, try for a primary IPv6 address ---
if [ -z "$IP_ADDR" ]; then
    # We do the same for IPv6 using Cloudflare's IPv6 address
    IP_ADDR=$(ip -6 route get 2606:4700:4700::1111 2>/dev/null | grep -oP 'src \K[0-9a-fA-F:]+')
fi

# --- If an IP (v4 or v6) was found, update the MOTD ---
if [ -n "$IP_ADDR" ]; then
    echo "Your IP address is $IP_ADDR" >> "$MOTD_FILE"
fi
