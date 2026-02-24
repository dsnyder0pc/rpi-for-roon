#!/bin/bash
# Description: Removes Argon ONE Fan controls (Appendix 1) and Argon-specific
#              IR hardware configs (Appendix 2b), but leaves the universal
#              roon-ir-remote Python service running for use with Flirc.
# Usage: Run as the 'audiolinux' user.

echo -e "\n\033[1mStarting Argon Cleanup & Flirc Pivot...\033[0m"

REBOOT_REQUIRED=0

# 1. Stop and disable Argon-specific services
echo "Stopping and disabling Argon services..."
sudo systemctl disable --now argononed.service 2>/dev/null
sudo systemctl disable --now ir-keymap.service 2>/dev/null

# 2. Remove systemd files and overrides
echo "Removing systemd service files..."
sudo rm -rf /etc/systemd/system/argononed.service.d
sudo rm -f /etc/systemd/system/ir-keymap.service
sudo systemctl daemon-reload

# 3. Remove the Argon Fan package
echo "Removing Argon packages..."
sudo pacman -Rns --noconfirm argonone-c-git 2>/dev/null

# 4. Remove hardware configuration files and udev rules
echo "Removing configuration files..."
sudo rm -f /etc/udev/rules.d/99-i2c.rules
sudo rm -f /etc/argononed.conf
sudo rm -f /etc/rc_keymaps/argon.toml

# 5. Clean up /boot/config.txt conditionally
if grep -q '^dtparam=i2c_arm=on' /boot/config.txt || grep -q '^dtoverlay=gpio-ir,gpio_pin=23' /boot/config.txt; then
    echo "Reverting /boot/config.txt hardware overlays..."
    sudo sed -i 's/^dtparam=i2c_arm=on/#dtparam=i2c_arm=on/' /boot/config.txt
    sudo sed -i '/^dtoverlay=gpio-ir,gpio_pin=23/d' /boot/config.txt
    REBOOT_REQUIRED=1
else
    echo "No active Argon hardware overlays found in /boot/config.txt."
fi

# 6. Restart the universal IR service just to be safe
if systemctl is-active --quiet roon-ir-remote.service; then
    echo "Restarting roon-ir-remote service for generic input..."
    sudo systemctl restart roon-ir-remote.service
fi

echo -e "\n\033[1;32mPivot complete!\033[0m"

# 7. Prompt for reboot if hardware overlays were removed
if [ "$REBOOT_REQUIRED" -eq 1 ]; then
    echo -e "\033[1;33mHardware overlays were removed from /boot/config.txt.\033[0m"
    read -rp "Would you like to reboot now to apply these changes? [y/N] " -n 1 REBOOT_ANSWER < /dev/tty
    echo ""
    if [[ "$REBOOT_ANSWER" =~ ^[Yy]$ ]]; then
        echo "Rebooting..."
        sudo reboot
    fi
fi
