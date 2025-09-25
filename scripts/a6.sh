#!/bin/bash

# --- Helper Functions ---

# Prints a formatted section header.
# Arguments:
#   $1: The title for the section.
print_header() {
    printf "\n--- %s ---\n" "$1"
}

# Prints CPU affinity for a given cpuset.
# Arguments:
#   $1: The title for the section (e.g., "Roon Bridge").
#   $2: The cpuset to query (e.g., "isolated1").
print_cpu_affinity() {
    local title="$1"
    local cpuset="$2"
    print_header "$title CPU Affinity"
    # The 'sudo' is kept here in case you run the script without it.
    sudo cset proc --list --set="$cpuset" --verbose
}

# Prints the IRQ affinity for end0.
print_irq_affinity() {
    print_header "end0 IRQ Affinity"
    printf "%-10s: %s\n" "IRQ 27" "$(sudo cat /proc/irq/27/smp_affinity_list)"
    printf "%-10s: %s\n" "IRQ 28" "$(sudo cat /proc/irq/28/smp_affinity_list)"
}

# --- Main Logic ---

# Use a 'case' statement to handle different hosts.
case "$HOSTNAME" in
  "diretta-target")
    echo "===== Status for: $HOSTNAME ====="

    rtprio=$(ps -o rtprio -C diretta_app_target | tail -n 1)
    printf "%-32s: %s\n" "Diretta ALSA Target App Priority" "$rtprio"

    print_cpu_affinity "Diretta ALSA Target" "isolated1"
    print_irq_affinity
    ;;

  *diretta*)
    echo "===== Status for: $HOSTNAME ====="

    timer_status=$(systemctl is-enabled rtapp.timer)
    printf "%-32s: %s\n" "Real Time App Timer Status" "$timer_status"

    print_cpu_affinity "Roon Bridge" "isolated1"
    print_cpu_affinity "Diretta ALSA Sync" "isolated2"
    print_irq_affinity
    ;;

  *)
    echo "Error: This script is not configured for host '$HOSTNAME'."
    exit 1
    ;;
esac

echo # Final newline for clean exit in the terminal
