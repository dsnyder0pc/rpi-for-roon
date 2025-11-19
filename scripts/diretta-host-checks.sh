#!/bin/bash
#
# Diretta Host QA Check Script v1.10
# (Updated to include Appendix 7 checks)
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
header() { echo -e "\n${C_BOLD}${C_YELLOW}--- $1: $2 ---${C_RESET}"; }
check_optional_section() {
    if eval "$1" &>/dev/null; then eval "$2"; else echo -e "\n${C_BOLD}${C_YELLOW}--- Skipping QA for $3 (Not Detected) ---\033[0m"; fi
}

# --- State for Optional Checks ---
PYTHON_CHECK_COMPLETE=0

# --- QA Check Functions for Optional Sections ---
run_python_checks() {
    if [[ $PYTHON_CHECK_COMPLETE -eq 0 ]]; then
        header 'Appendices 2 & 4' 'Optional: Python Environment'
        check 'pyenv is installed for user audiolinux' '[ -d /home/audiolinux/.pyenv ]'
        check 'A python version is installed via pyenv' 'ls /home/audiolinux/.pyenv/versions | grep -q "[0-9]"'
        check '.bashrc is configured for pyenv' 'grep -q "pyenv init" /home/audiolinux/.bashrc'
        PYTHON_CHECK_COMPLETE=1
    fi
}
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
run_appendix2_checks() {
    check_optional_section "[ -d /home/audiolinux/.pyenv ]" "run_python_checks" "Python Environment"
    header "Appendix 2" "Optional: IR Remote Control"
    check "'audiolinux' user is in 'input' group" "groups audiolinux | grep -q '\<input\>'"
    check "'roon-ir-remote' directory exists" "[ -d /home/audiolinux/roon-ir-remote ]"
    check "Roon IR config 'app_info.json' exists" "[ -f /home/audiolinux/roon-ir-remote/app_info.json ]"
    check "'roon-ir-remote' service is enabled" "systemctl is-enabled roon-ir-remote.service"
    check "'roon-ir-remote' service is active" "systemctl is-active roon-ir-remote.service"
    check "'set-roon-zone' script is up-to-date" "[ -x /usr/local/bin/set-roon-zone ] && [[ \$(md5sum /usr/local/bin/set-roon-zone | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone | md5sum | awk '{print \$1}') ]]"
    # Only check for Argon IR specifics if the dtoverlay is active in /boot/config.txt
    if grep -q '^dtoverlay=gpio-ir,gpio_pin=23' /boot/config.txt; then
        header "Appendix 2b" "Optional: Argon IR Receiver"
        check "/boot/config.txt enables Argon IR" "grep -q '^dtoverlay=gpio-ir,gpio_pin=23' /boot/config.txt"
        check "Argon IR keymap '/etc/rc_keymaps/argon.toml' exists" "[ -f /etc/rc_keymaps/argon.toml ]"
        check "'ir-keymap' service is enabled" "systemctl is-enabled ir-keymap.service"
    fi
}
run_appendix4_checks() {
    check_optional_section "[ -d /home/audiolinux/.pyenv ]" "run_python_checks" "Python Environment"
    header "Appendix 4" "Optional: Purist Mode Web UI"
    check "'avahi-daemon' service is enabled" "systemctl is-enabled avahi-daemon.service"
    check "Avahi is configured for USB LAN" "[ -f /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf ]"
    check "Web UI SSH key exists" "[ -f /home/audiolinux/.ssh/purist_app_key ]"
    check "Web UI app file is up-to-date" "[ -f /home/audiolinux/purist-mode-webui/app.py ] && [[ \$(md5sum /home/audiolinux/purist-mode-webui/app.py | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py | md5sum | awk '{print \$1}') ]]"
    check "Python has port binding capability" "getcap \$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python) | grep -q 'cap_net_bind_service.ep'"
    check "Web UI sudoers file exists" "[ -f /etc/sudoers.d/webui-restarts ]"
    check "'purist-webui' service is enabled" "systemctl is-enabled purist-webui.service"
    check "'purist-webui' service is active" "systemctl is-active purist-webui.service"
}
run_appendix6_checks() {
    header "Appendix 6" "Advanced Realtime Performance Tuning"
    check "'rtapp.timer' service is disabled" "! systemctl is-enabled rtapp.timer"
    check "CPU isolation is set to cores 2-3" "[[ \$(cset set --list 2>/dev/null | grep 'isolated1' | awk '{print \$2}') == '2-3' ]]"
    check "RoonBridge is running on isolated cores" "cset proc --list --set=isolated1 2>/dev/null | grep -q 'RoonBridge'"
    check "syncAlsa is running on isolated cores" "cset proc --list --set=isolated1 2>/dev/null | grep -q 'syncAlsa'"
    check "Network IRQs (end0) are pinned to cores 2-3 (affinity 'c')" "for irq in \$(grep 'end0' /proc/interrupts | awk '{print \$1}' | tr -d :); do grep -q 'c$' /proc/irq/\$irq/smp_affinity || exit 1; done"
}

# --- [NEW] Appendix 7 Function ---
run_appendix7_checks() {
    header "Appendix 7" "Optional: Event-Driven CPU Hooks"
    check "'isolated_app.timer' is disabled" "! systemctl is-enabled isolated_app.timer 2>/dev/null"
    check "Roon hook for 'isolated_app.sh' is set" "grep -qr 'ExecStartPost=/opt/scripts/system/isolated_app.sh' /etc/systemd/system/roonbridge.service.d/"
    check "Roon reload hook for 'isolated_app.sh' is set" "grep -qr 'ExecReloadPost=/opt/scripts/system/isolated_app.sh' /etc/systemd/system/roonbridge.service.d/"
    check "Diretta hook for 'isolated_app.sh' is set" "grep -qr 'ExecStartPost=/opt/scripts/system/isolated_app.sh' /etc/systemd/system/diretta_alsa.service.d/"
    check "Diretta reload hook for 'isolated_app.sh' is set" "grep -qr 'ExecReloadPost=/opt/scripts/system/isolated_app.sh' /etc/systemd/system/diretta_alsa.service.d/"
}
# --- End of new function ---

# --- Main Script ---
if [ "$EUID" -ne 0 ]; then echo -e "${C_RED}Please run this script with sudo or as root.${C_RESET}"; exit 1; fi
echo -e "${C_BOLD}Starting Diretta Host Configuration Quality Assurance Check...${C_RESET}"

header "Section 3" "Core System Configuration"
check "/etc/machine-id is not empty" "[ -s /etc/machine-id ]"

header "Section 4" "System Updates & Time"
check "'chrony' package is installed" "pacman -Q chrony"
check "'chronyd' service is enabled" "systemctl is-enabled chronyd.service"
check "'chronyd' service is active" "systemctl is-active chronyd.service"
check "Timezone is configured" "[ -e /etc/localtime ] && [[ \$(readlink /etc/localtime) == ../usr/share/zoneinfo/* ]]"
check "'dnsutils' package is installed (for menu updates)" "pacman -Q dnsutils"

header "Section 5" "Point-to-Point Network Configuration"
check "P2P network file 'end0.network' exists" "[ -f /etc/systemd/network/end0.network ]"
check "P2P network file contains correct IP" "grep -q 'Address=172.20.0.1/24' /etc/systemd/network/end0.network"
check "USB LAN network file 'enp.network' exists" "[ -f /etc/systemd/network/enp.network ]"
check "USB LAN network file is set for DHCP" "grep -q 'DHCP=yes' /etc/systemd/network/enp.network"
check "Old generic network files are removed" "! [ -f /etc/systemd/network/en.network ] && ! [ -f /etc/systemd/network/auto.network ] && ! [ -f /etc/systemd/network/eth.network ]"
check "/etc/hosts contains 'diretta-target' entry" "grep -q '172.20.0.2.*diretta-target' /etc/hosts"
check "IP forwarding is enabled in sysctl.d" "grep -q 'net.ipv4.ip_forward=1' /etc/sysctl.d/99-ip-forwarding.conf"
check "IP forwarding is active in kernel" "[[ \$(cat /proc/sys/net/ipv4/ip_forward) -eq 1 ]]"
check "'nftables' package is installed" "pacman -Q nftables"
check "'nftables' service is enabled" "systemctl is-enabled nftables.service"
check "'nftables' service has not failed" "! systemctl is-failed --quiet nftables.service"
check "nftables config file '/etc/nftables.conf' exists" "[ -f /etc/nftables.conf ]"
check "nftables config contains DNAT rule (5101 -> 5001)" "grep -q 'tcp dport 5101 dnat to 172.20.0.2:5001' /etc/nftables.conf"
check "nftables config contains FORWARD rule (-> 5001)" "grep -q 'ip daddr 172.20.0.2 tcp dport 5001 ct state new accept' /etc/nftables.conf"
check "nftables config contains MASQUERADE rules" "grep -q 'oifname \"enp\*\" masquerade' /etc/nftables.conf && grep -q 'oifname \"wlp\*\" masquerade' /etc/nftables.conf"
check "Old 'iptables' service is disabled" "! systemctl is-enabled iptables.service 2>/dev/null"
check "Old 'iptables' rule file is removed" "! [ -f /etc/iptables/iptables.rules ] 2>/dev/null"
check "USB Ethernet udev rule exists" "[ -f /etc/udev/rules.d/99-ax88179a.rules ]"
check "MOTD update script is up-to-date" "[ -f /opt/scripts/update/update_motd.sh ] && [[ \$(md5sum /opt/scripts/update/update_motd.sh | awk '{print \$1}') == \$(curl -sL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh | md5sum | awk '{print \$1}') ]]"

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
check "'diretta-alsa-daemon' package is installed" "pacman -Q diretta-alsa-daemon"
check "'diretta-alsa-dkms' package is installed" "pacman -Q diretta-alsa-dkms"
check "'diretta_alsa' service is enabled" "systemctl is-enabled diretta_alsa.service"
check "'diretta_alsa' service is active" "systemctl is-active diretta_alsa.service"
check "Diretta is configured for 'end0' interface" "grep -q 'Interface=end0' /opt/diretta-alsa/setting.inf"
check "Diretta service is set to auto-restart" "[ -f /etc/systemd/system/diretta_alsa.service.d/restart.conf ] && grep -q 'Restart=on-failure' /etc/systemd/system/diretta_alsa.service.d/restart.conf"

header "Section 8a" "Diretta Compiler Toolchain"
check "Compiler profile script exists" "[ -f /etc/profile.d/llvm_diretta.sh ]"
check "Compiler profile script sets PATH" "grep -q 'export PATH=.*bin:\$PATH' /etc/profile.d/llvm_diretta.sh"
check "pacman.conf ignores 'clang'" "grep -Pq '^IgnorePkg\s*=\s*.*(clang|clang[0-9]+)' /etc/pacman.conf"
check "pacman.conf ignores 'llvm'" "grep -Pq '^IgnorePkg\s*=\s*.*(llvm|llvm[0-9]+)' /etc/pacman.conf"
check "pacman.conf ignores 'lld'" "grep -Pq '^IgnorePkg\s*=\s*.*(lld|lld[0-9]+)' /etc/pacman.conf"
check "pacman.conf ignores 'diretta-alsa-daemon'" "grep -Pq '^IgnorePkg\s*=\s*.*diretta-alsa-daemon' /etc/pacman.conf"
check "pacman.conf ignores 'diretta-alsa-dkms'" "grep -Pq '^IgnorePkg\s*=\s*.*diretta-alsa-dkms' /etc/pacman.conf"

header "Section 9" "Roon Integration"
check "'roonbridge' is installed" "pacman -Q roonbridge"
check "'roonbridge' service is enabled" "systemctl is-enabled roonbridge.service"
check "'roonbridge' service is active" "systemctl is-active roonbridge.service"

# --- Optional Appendix Checks ---
check_optional_section "pacman -Q argonone-c-git" "run_appendix1_checks" "Appendix 1 (Argon ONE Fan)"
check_optional_section "[ -d /home/audiolinux/roon-ir-remote ]" "run_appendix2_checks" "Appendix 2 (IR Remote)"
check_optional_section "[ -d /home/audiolinux/purist-mode-webui ]" "run_appendix4_checks" "Appendix 4 (Web UI)"
check_optional_section "cset set --list 2>/dev/null | grep -q 'isolated1'" "run_appendix6_checks" "Appendix 6 (Realtime Tuning)"
# --- [NEW] Appendix 7 Check Call ---
check_optional_section "[ -d /etc/systemd/system/roonbridge.service.d ]" "run_appendix7_checks" "Appendix 7 (Event-Driven Hooks)"
# --- End of new call ---

echo -e "\n${C_BOLD}QA Check Complete.${C_RESET}\n"
