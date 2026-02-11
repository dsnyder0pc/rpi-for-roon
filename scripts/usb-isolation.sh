#!/bin/bash
# Diretta Target USB Optimization for AudioLinux
# Smart Hardware Detection & Dynamic IRQ Affinity
# NOTE: This optimization is strictly for Raspberry Pi 5.

ISO_CONFIG="/opt/configuration/isolated.conf"
ISO_CORES="2,3"
ISO_CORES_DASH="2-3"

echo "--- Diretta Target Smart USB Optimization ---"

# 1. Hardware Detection
MODEL=$(tr -d '\0' < /proc/device-tree/model)
echo "System: $MODEL"

# 2. Platform Validation
if [[ "$MODEL" == *"Raspberry Pi 4"* ]]; then
    echo "Notice: Raspberry Pi 4 detected."
    echo "USB IRQ (29) is hardware-locked on this platform."
    echo "Skipping USB isolation optimization (not applicable)."
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
