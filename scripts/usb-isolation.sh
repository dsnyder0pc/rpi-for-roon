#!/bin/bash
# Diretta Target USB Optimization for AudioLinux
# Smart Hardware Detection & Dynamic IRQ Affinity
# NOTE: Raspberry Pi 5 steers the USB IRQ itself; Raspberry Pi 4 can only
# move the IRQ's handler thread (see below).

ISO_CONFIG="/opt/configuration/isolated.conf"
ISO_CORES="2,3"
ISO_CORES_DASH="2-3"
RPI4_UNIT="/etc/systemd/system/usb-irq-thread-isolation.service"

echo "--- Diretta Target Smart USB Optimization ---"

# 0. Target only. A Host's USB Ethernet uplink busies an xHCI IRQ just like a
# DAC does, so on a Host this would pin the uplink onto the audio cores.
if [[ "$(hostname)" != "diretta-target" ]]; then
    echo "Error: This script is for the Diretta Target only (this is '$(hostname)')."
    echo "Nothing was changed. Run it on the Target, while music is playing."
    exit 1
fi

# 1. Hardware Detection
MODEL=$(tr -d '\0' < /proc/device-tree/model)
echo "System: $MODEL"

# 2. Raspberry Pi 4: pin the xHCI IRQ thread instead of the IRQ
#
# Every RPi4 USB port sits behind the VL805 xHCI on PCIe. Its interrupt is an
# MSI that the PCIe driver demultiplexes from one chained GIC interrupt, so
# /proc/irq/<n>/smp_affinity_list refuses writes (EPERM) and the hard IRQ
# always lands on CPU0. On the PREEMPT_RT kernel, though, the hard IRQ only
# wakes a handler thread, irq/<n>-xhci_hcd, and that thread does the actual
# USB work. It can be moved, and it stays where it is put: the kernel only
# re-syncs it to the IRQ's mask when that mask changes, which it cannot.
# On an RPi5 the same thread follows its IRQ onto the isolated cores, so this
# puts the USB work in the same place. The difference is that each USB event
# now reaches the isolated cores as a wake-up from CPU0.
#
# A boot-time unit reapplies it, since thread affinity does not survive a
# reboot and nothing in AudioLinux sets it. There is only one xHCI on an RPi4,
# so no playback is needed to find the DAC's controller.
if [[ "$MODEL" == *"Raspberry Pi 4"* ]]; then
    echo "Raspberry Pi 4 detected: the USB IRQ cannot be steered on this board."
    echo "Pinning the xHCI IRQ handler thread to cores $ISO_CORES_DASH instead."

    if ! pgrep -x 'irq/[0-9]+-xhci_hcd' > /dev/null; then
        echo "Error: No xHCI IRQ thread found. This needs the AudioLinux realtime kernel."
        exit 1
    fi

    sudo tee "$RPI4_UNIT" > /dev/null <<EOF
[Unit]
Description=Pin the xHCI IRQ thread to the isolated audio cores (Raspberry Pi 4)

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'for p in \$\$(pgrep -x "irq/[0-9]+-xhci_hcd"); do taskset -pc $ISO_CORES_DASH \$\$p || exit 1; done'
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable usb-irq-thread-isolation.service > /dev/null 2>&1
    if ! sudo systemctl restart usb-irq-thread-isolation.service; then
        echo "Error: Could not pin the xHCI IRQ thread."
        exit 1
    fi

    for P in $(pgrep -x 'irq/[0-9]+-xhci_hcd'); do
        echo "$(cat /proc/$P/comm) (pid $P) -> cores $(taskset -pc $P | awk '{print $NF}')"
    done
    echo "Done. The boot-time unit reapplies this after every reboot."
    exit 0
fi

# 3. Dynamic IRQ Discovery (RPi5 Logic Only)
TARGET_IRQS=""
TARGET_DEVS=""

if [[ "$MODEL" == *"Raspberry Pi 5"* ]]; then
    for BUS in usb1 usb3; do
        MATCH=$(grep "xhci-hcd:$BUS" /proc/interrupts)
        if [ -n "$MATCH" ]; then
            # SRE Logic: Check if the IRQ has clocked more than 100 hits
            HITS=$(echo "$MATCH" | awk '{sum=0; for(i=2;i<=5;i++) sum+=$i; print sum}')
            if [ "$HITS" -gt 100 ]; then
                IRQ=$(echo "$MATCH" | awk -F: '{print $1}' | tr -d ' ')
                DEV=$(echo "$MATCH" | awk '{print $NF}')
                TARGET_IRQS="$TARGET_IRQS $IRQ"
                TARGET_DEVS="$TARGET_DEVS $DEV"
                echo "Detected Active DAC path on $BUS (IRQ $IRQ)"
            fi
        fi
    done
fi

# 4. Final Validation & Runtime Application
TARGET_IRQS=$(echo "$TARGET_IRQS" | xargs -n1 | sort -u | xargs)
TARGET_DEVS=$(echo "$TARGET_DEVS" | xargs -n1 | sort -u | xargs)

if [ -z "$TARGET_IRQS" ]; then
    echo "Error: No active USB audio stream detected. Play music and try again."
    exit 1
fi

for IRQ in $TARGET_IRQS; do
    echo "Applying runtime affinity: IRQ $IRQ -> Cores $ISO_CORES_DASH"
    echo "$ISO_CORES_DASH" | sudo tee "/proc/irq/$IRQ/smp_affinity_list" > /dev/null
done

# 5. Permanent Config Update
if [ -f "$ISO_CONFIG" ] && grep -q "ISOLATED1=\"$ISO_CORES\"" "$ISO_CONFIG"; then
    echo ""
    echo "Updating AudioLinux config for persistence..."
    sudo cp "$ISO_CONFIG" "${ISO_CONFIG}.bak"

    for IRQ in $TARGET_IRQS; do
        if ! grep -qE "IRQ1=.*(\"|[[:space:]])${IRQ}([[:space:]]|\")" "$ISO_CONFIG"; then
            sudo sed -i "/^IRQ1=/ s/\"$/ $IRQ\"/" "$ISO_CONFIG"
            echo "Added IRQ $IRQ to config."
        fi
    done

    for DEV in $TARGET_DEVS; do
        if ! grep -qE "DEVICES1=.*(\"|[[:space:]])${DEV}([[:space:]]|\")" "$ISO_CONFIG"; then
            sudo sed -i "/^DEVICES1=/ s/\"$/ $DEV\"/" "$ISO_CONFIG"
            echo "Added device $DEV to config."
        fi
    done

    sudo sed -i 's/  */ /g' "$ISO_CONFIG"
    sudo sed -i 's/="/="/g' "$ISO_CONFIG"
    echo "Done. persistent config updated."
fi
