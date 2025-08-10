#!/bin/bash
#
# Diretta Target QA Check Script
#
# This script verifies the configuration of a Diretta Target based on the
# instructions in the RPi for Roon guide. It should be run with sudo.
#
# Usage:
# ssh diretta-target "curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/diretta-target-checks.sh | sudo bash"

# --- Colors and Formatting ---
C_RESET='\033[0m'
C_RED='\033[0;31m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_BLUE='\033[0;34m'
C_BOLD='\033[1m'

# --- Helper Functions ---

# Prints a pass/fail message for a check.
# $1: Description of the check.
# $2: The command to execute for the check.
#     The command should return 0 for success, non-zero for failure.
check() {
    local description="$1"
    local command_to_run="$2"

    printf "  ${C_BLUE}*${C_RESET} %-68s" "$description"
    if eval "$command_to_run" &>/dev/null; then
        printf "[${C_GREEN}PASS${C_RESET}]\n"
    else
        printf "[${C_RED}FAIL${C_RESET}]\n"
    fi
}

# Prints a section header.
# $1: Section/Appendix number
# $2: Section/Appendix title
header() {
    echo -e "\n${C_BOLD}${C_YELLOW}--- $1: $2 ---${C_RESET}"
}

# --- Main Script ---
# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo -e "${C_RED}Please run this script with sudo or as root.${C_RESET}"
  exit 1
fi

echo -e "${C_BOLD}Starting Diretta Target Configuration Quality Assurance Check...${C_RESET}"

# --- Section 3: Core System Configuration ---
header "Section 3" "Core System Configuration"
check "Hostname is 'diretta-target'" "[[ \$(hostname) == 'diretta-target' ]]"
check "/etc/machine-id is not empty" "[ -s /etc/machine-id ]"

# --- Section 4: System Updates & Time ---
header "Section 4" "System Updates & Time"
check "'chrony' package is installed" "pacman -Q chrony"
check "'chronyd' service is enabled" "systemctl is-enabled chronyd.service"
# Note: chronyd may be inactive if Purist Mode is on, so we don't check for active state.
check "Timezone is configured" "[ -e /etc/localtime ] && [[ \$(readlink /etc/localtime) == ../usr/share/zoneinfo/* ]]"

# --- Section 5: Point-to-Point Network ---
header "Section 5" "Point-to-Point Network Configuration"
check "P2P network file 'end0.network' exists" "[ -f /etc/systemd/network/end0.network ]"
check "P2P network file contains correct IP" "grep -q 'Address=172.20.0.2/24' /etc/systemd/network/end0.network"
check "P2P network file contains correct Gateway" "grep -q 'Gateway=172.20.0.1' /etc/systemd/network/end0.network"
check "Old generic network file is removed" "! [ -f /etc/systemd/network/en.network ]"
check "/etc/hosts contains 'diretta-host' entry" "grep -q '172.20.0.1.*diretta-host' /etc/hosts"

# --- Section 7: Boot Filesystem Clean ---
header "Section 7" "Boot Filesystem Integrity"
check "Boot repair script is up-to-date" "[ -x /usr/local/sbin/check-and-repair-boot.sh ] && [[ \$(md5sum /usr/local/sbin/check-and-repair-boot.sh | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh | md5sum | awk '{print \$1}') ]]"
check "'boot-repair' service file exists" "[ -f /etc/systemd/system/boot-repair.service ]"
check "'boot-repair' service is enabled" "systemctl is-enabled boot-repair.service"

# --- Section 8: Diretta & Journald ---
header "Section 8" "Diretta Software & System Logging"
check "Journald is set to volatile storage" "grep -q '^Storage=volatile' /etc/systemd/journald.conf"
check "'diretta-alsa-target' is installed" "[ -d /opt/diretta-alsa-target ]"
check "'diretta_alsa_target' service is enabled" "systemctl is-enabled diretta_alsa_target.service"
check "'diretta_alsa_target' service is active" "systemctl is-active diretta_alsa_target.service"
check "Diretta license appears to be activated" "ls /opt/diretta-alsa-target/ | grep -qv '^diretta'"

# --- Appendix 1: Optional Argon ONE Fan Control ---
if [ -f /etc/systemd/system/argononed.service ]; then
    header "Appendix 1" "Optional: Argon ONE Fan Control"
    check "/boot/config.txt enables i2c" "grep -q '^dtparam=i2c_arm=on' /boot/config.txt"
    check "i2c udev rule exists" "[ -f /etc/udev/rules.d/99-i2c.rules ]"
    check "'argonone-c-git' package is installed" "pacman -Q argonone-c-git"
    check "'argononed' service is enabled" "systemctl is-enabled argononed.service"
    # Note: argononed may be inactive if Purist Mode is on, so we don't check for active state.
fi

# --- Appendix 3: Optional Purist Mode ---
if [ -f /usr/local/bin/purist-mode ]; then
    header "Appendix 3" "Optional: Purist Mode"
    check "'purist-mode' script is up-to-date" "[ -x /usr/local/bin/purist-mode ] && [[ \$(md5sum /usr/local/bin/purist-mode | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode | md5sum | awk '{print \$1}') ]]"
    check "Login status message script exists" "[ -f /etc/profile.d/purist-status.sh ]"
    check "Purist revert-on-boot service is enabled" "systemctl is-enabled purist-mode-revert-on-boot.service"
    check "Menu wrapper alias is in .bashrc" "grep -q 'alias menu=.menu_wrapper' /home/audiolinux/.bashrc"
fi

# --- Appendix 4: Optional Purist Mode Web UI Backend ---
if id "purist-app" &>/dev/null; then
    header "Appendix 4" "Optional: Purist Mode Web UI (Backend)"
    check "'purist-app' user exists" "id purist-app"
    check "'pm-get-status' script exists" "[ -x /usr/local/bin/pm-get-status ]"
    check "'pm-toggle-mode' script exists" "[ -x /usr/local/bin/pm-toggle-mode ]"
    check "'pm-toggle-auto' script exists" "[ -x /usr/local/bin/pm-toggle-auto ]"
    check "'pm-restart-target' script exists" "[ -x /usr/local/bin/pm-restart-target ]"
    check "Sudoers file for 'purist-app' exists" "[ -f /etc/sudoers.d/purist-app ]"
    check "SSH authorized_keys for 'purist-app' exists" "[ -f /home/purist-app/.ssh/authorized_keys ]"
    check "SSH authorized_keys has security restrictions" "grep -q 'command=\"sudo' /home/purist-app/.ssh/authorized_keys"
fi


echo -e "\n${C_BOLD}QA Check Complete.${C_RESET}\n"
