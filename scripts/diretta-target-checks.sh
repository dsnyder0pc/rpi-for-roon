#!/bin/bash
#
# Diretta Target QA Check Script v1.7
#

# --- Colors and Formatting ---
C_RESET=$'\033[0m'
C_RED=$'\033[0;31m'
C_GREEN=$'\033[0;32m'
C_YELLOW=$'\033[1;33m'
C_BLUE=$'\033[0;34m'
C_BOLD=$'\033[1m'

# --- Helper Functions ---
check() {
    printf "  ${C_BLUE}*${C_RESET} %-68s" "$1"
    if eval "$2" &>/dev/null; then
        printf '[%sPASS%s]\n' "$C_GREEN" "$C_RESET"
    else
        printf '[%sFAIL%s]\n' "$C_RED" "$C_RESET"
    fi
}
check_status() {
    printf "  ${C_BLUE}*${C_RESET} %-68s" "$1"
    if eval "$2" &>/dev/null; then
        printf '[%s%s%s]\n' "$C_GREEN" "$3" "$C_RESET"
    else
        printf '[%s%s%s]\n' "$C_YELLOW" "$4" "$C_RESET"
    fi
}
header() { echo -e "\n${C_BOLD}${C_YELLOW}--- $1: $2 ---${C_RESET}"; }
check_optional_section() {
    if eval "$1" &>/dev/null; then eval "$2"; else echo -e "\n${C_BOLD}${C_YELLOW}--- Skipping QA for $3 (Not Detected) ---\033[0m"; fi
}

# --- QA Check Functions for Optional Sections ---
run_appendix1_checks() {
    header "Appendix 1" "Optional: Argon ONE Fan Control"
    check "/boot/config.txt enables i2c" "grep -q '^dtparam=i2c_arm=on' /boot/config.txt"
    check "i2c udev rule exists" "[ -f /etc/udev/rules.d/99-i2c.rules ]"
    check "'argonone-c-git' package is installed" "pacman -Q argonone-c-git"
    check "'argononed' service is enabled" "systemctl is-enabled argononed.service"
    check "'argononed' service is active" "systemctl is-active argononed.service"
    check "Software mode override uses 'active wait' loop" "grep -q 'while.*i2c-1' /etc/systemd/system/argononed.service.d/software-mode.conf"
    check "Late-start override file exists" "[ -f /etc/systemd/system/argononed.service.d/override.conf ]"
    check "Late-start override is set for 'multi-user.target'" "grep -q 'After=multi-user.target' /etc/systemd/system/argononed.service.d/override.conf"
    check "Custom fan schedule '/etc/argononed.conf' exists" "[ -f /etc/argononed.conf ]"
}
run_appendix3_checks() {
    header "Appendix 3" "Optional: Purist Mode"
    check "'purist-mode' script is up-to-date" "[ -x /usr/local/bin/purist-mode ] && [[ \$(md5sum /usr/local/bin/purist-mode | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode | md5sum | awk '{print \$1}') ]]"
    check "Login status message script exists" "[ -f /etc/profile.d/purist-status.sh ]"
    check "Purist revert-on-boot service is enabled" "systemctl is-enabled purist-mode-revert-on-boot.service"
    check "Menu wrapper alias is in .bashrc" "grep -q 'alias menu=.menu_wrapper' /home/audiolinux/.bashrc"
}
run_appendix4_checks() {
    header "Appendix 4" "Optional: Purist Mode Web UI (Backend)"
    check "'purist-app' user exists" "id purist-app"
    check "'pm-get-status' script exists" "[ -x /usr/local/bin/pm-get-status ]"
    check "'pm-get-license-url' script exists" "[ -x /usr/local/bin/pm-get-license-url ]"
    check "'pm-toggle-mode' script exists" "[ -x /usr/local/bin/pm-toggle-mode ]"
    check "'pm-toggle-auto' script exists" "[ -x /usr/local/bin/pm-toggle-auto ]"
    check "'pm-restart-target' script exists" "[ -x /usr/local/bin/pm-restart-target ]"
    check "'create-diretta-cache.sh' script exists" "[ -x /usr/local/bin/create-diretta-cache.sh ]"
    check "Systemd drop-in for cache creation exists" "[ -f /etc/systemd/system/purist-mode-revert-on-boot.service.d/create-cache.conf ]"
    check "Sudoers file for 'purist-app' exists" "[ -f /etc/sudoers.d/purist-app ]"
    check "Sudoers allows 'pm-get-license-url'" "grep -q 'NOPASSWD: /usr/local/bin/pm-get-license-url' /etc/sudoers.d/purist-app"
    check "SSH authorized_keys for 'purist-app' exists" "[ -f /home/purist-app/.ssh/authorized_keys ]"
    check "SSH authorized_keys has security restrictions" "grep -q 'command=\"sudo' /home/purist-app/.ssh/authorized_keys"
}
run_appendix6_checks() {
    header "Appendix 6" "Advanced Realtime Performance Tuning"
    check "Diretta app realtime priority is set to 70" "[[ \$(ps -o rtprio -C diretta_app_target | tail -n 1 | tr -d ' ') -eq 70 ]]"
    check "CPU isolation is set to cores 2 and 3" "[[ \$(cset set --list 2>/dev/null | grep 'isolated1' | awk '{print \$2}') == '2-3' ]]"
    check "Diretta app is running on the isolated core" "cset proc --list --set=isolated1 2>/dev/null | grep -q 'diretta_app_target'"
}

# --- Main Script ---
if [ "$EUID" -ne 0 ]; then echo -e "${C_RED}Please run this script with sudo or as root.${C_RESET}"; exit 1; fi
echo -e "${C_BOLD}Starting Diretta Target Configuration Quality Assurance Check...${C_RESET}"

header "Section 3" "Core System Configuration"
check "Hostname is 'diretta-target'" "[[ \$(hostname) == 'diretta-target' ]]"
check "/etc/machine-id is not empty" "[ -s /etc/machine-id ]"

header "Section 4" "System Updates & Time"
check "'chrony' package is installed" "pacman -Q chrony"
check "'chronyd' service is enabled" "systemctl is-enabled chronyd.service"
check "Timezone is configured" "[ -e /etc/localtime ] && [[ \$(readlink /etc/localtime) == ../usr/share/zoneinfo/* ]]"

header "Section 5" "Point-to-Point Network Configuration"
check "P2P network file 'end0.network' exists" "[ -f /etc/systemd/network/end0.network ]"
check "P2P network file contains correct IP" "grep -q 'Address=172.20.0.2/24' /etc/systemd/network/end0.network"
check "P2P network file contains correct Gateway" "grep -q 'Gateway=172.20.0.1' /etc/systemd/network/end0.network"
check "Old generic network file is removed" "! [ -f /etc/systemd/network/en.network ]"
check "/etc/hosts contains 'diretta-host' entry" "grep -q '172.20.0.1.*diretta-host' /etc/hosts"

header "Section 7" "Common System Optimizations"
check "'shadow' service is not in a failed state" "! systemctl is-failed --quiet shadow.service"
check "sudoers rule order is correct" "awk '/^audiolinux ALL=\\(ALL\\) ALL$/ {u=NR} /^@includedir/ {i=NR} END {exit !(u && i && u < i)}' /etc/sudoers"
check "'wait-online' service is disabled (for fast boot)" "! systemctl is-enabled systemd-networkd-wait-online.service"
check "MOTD service actively waits for a default route" "[ -f /etc/systemd/system/update_motd.service.d/wait-for-ip.conf ] && grep -q 'while.*ip route' /etc/systemd/system/update_motd.service.d/wait-for-ip.conf"
check "Boot repair script is up-to-date" "[ -x /usr/local/sbin/check-and-repair-boot.sh ] && [[ \$(md5sum /usr/local/sbin/check-and-repair-boot.sh | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh | md5sum | awk '{print \$1}') ]]"
check "'boot-repair' service file exists" "[ -f /etc/systemd/system/boot-repair.service ]"
check "'boot-repair' service is enabled" "systemctl is-enabled boot-repair.service"

header "Section 8" "Diretta Software & System Logging"
check "Journald is set to volatile storage" "grep -q '^Storage=volatile' /etc/systemd/journald.conf"
check "'diretta-alsa-target' is installed" "[ -d /opt/diretta-alsa-target ]"
check "'diretta_alsa_target' service is enabled" "systemctl is-enabled diretta_alsa_target.service"
check "'diretta_alsa_target' service is active" "systemctl is-active diretta_alsa_target.service"
check "USB DAC/DDC is configured and detected" "journalctl -b -u diretta_alsa_target.service | grep -q 'DAC Name :'"
check_status "Diretta Target License Status" "ls /opt/diretta-alsa-target/ | grep -qv '^diretta'" "activated" "limited"

# --- Optional Appendix Checks ---
check_optional_section "pacman -Q argonone-c-git" "run_appendix1_checks" "Appendix 1 (Argon ONE Fan)"
check_optional_section "[ -f /usr/local/bin/purist-mode ]" "run_appendix3_checks" "Appendix 3 (Purist Mode)"
check_optional_section "id purist-app" "run_appendix4_checks" "Appendix 4 (Web UI Backend)"
check_optional_section "cset set --list 2>/dev/null | grep -q 'isolated1'" "run_appendix6_checks" "Appendix 6 (Realtime Tuning)"

echo -e "\n${C_BOLD}QA Check Complete.${C_RESET}\n"
