#!/bin/bash
################################################################################
#
# How to run:
# curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/misc/dcs-hotfix.sh | bash
#
# Optional Check:
# curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
#
################################################################################

patch_target() {
    local was_active=false
    # Check the initial state of Purist Mode by looking for the backup file.
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        was_active=true
    fi
    # If Purist Mode was active, temporarily revert it.
    if [ "$was_active" = true ]; then
        echo "Checking credentials to manage Purist Mode..."
        sudo -v
        echo "Temporarily disabling Purist Mode to run menu..."
        /usr/local/bin/purist-mode --revert > /dev/null 2>&1 # Revert quietly
    fi

    cd || return
    echo "- Updating Purist Mode CLI Tool"
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
    sudo install -m 0755 purist-mode /usr/local/bin
    rm purist-mode

    echo "- Updating the Delayed Diretta License Cache Creation Script"
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    echo "- Updating the Diretta License Cache Collector Service"
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta-cache.service
[Unit]
Description=Asynchronous Diretta License Cache Collector
After=network.target purist-mode-revert-on-boot.service
Before=purist-mode-auto.service

[Service]
Type=oneshot
RemainAfterExit=yes
# Block execution cleanly here until the Host replies to a ping
TimeoutStartSec=infinity
ExecStartPre=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done"
ExecStart=/usr/local/bin/create-diretta-cache.sh
Restart=no

[Install]
WantedBy=multi-user.target
EOT

    echo "- Updating the Delayed Auto-Activation Service"
    cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-auto.service
[Unit]
Description=Activate Purist Mode 60 seconds after boot
After=diretta-cache.service

[Service]
Type=oneshot
TimeoutStartSec=infinity
ExecStart=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done && sleep 60 && /usr/local/bin/purist-mode"

[Install]
WantedBy=multi-user.target
EOT

    sudo systemctl daemon-reload
    sudo systemctl enable purist-mode-auto.service
    sudo systemctl enable diretta-cache.service

    # If Purist Mode was active before, re-enable it now.
    if [ "$was_active" = true ]; then
        echo "Re-activating Purist Mode..."
        /usr/local/bin/purist-mode > /dev/null 2>&1 # Activate quietly
        echo "Purist Mode is active again."
    fi
}

patch_host() {
    cd || return
    echo "- Updating SSH Config"
    mkdir -p ~/.ssh
    chmod go-rwx ~/.ssh
    cat <<'EOT' > ~/.ssh/config
Host diretta-target target
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    GlobalKnownHostsFile /dev/null
    LogLevel ERROR
    ConnectTimeout 5
EOT
    chmod -R go-rwx ~/.ssh

    echo "- Updating Purist Mode Web App"
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    sudo systemctl daemon-reload
    sudo systemctl restart purist-webui.service
}

if [[ "$HOSTNAME" == "diretta-target" ]]; then
    echo "Diretta Target detected. Patching Target..."
    patch_target
elif [[ "$HOSTNAME" == *diretta* ]]; then
    echo "Diretta Host detected ('${HOSTNAME}'). Patching Host..."
    patch_host
else
    echo "Error: Could not determine if this is a Diretta Host or Target."
    echo "Please ensure the hostname contains 'diretta' (for a Host) or is 'diretta-target'."
    exit 1
fi
