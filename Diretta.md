# Building a Dedicated Diretta Link with Audiolinux on Raspberry Pi

This guide provides comprehensive, step-by-step instructions for configuring two Raspberry Pi devices as a dedicated Diretta Host and Diretta Target. This setup uses a direct, point-to-point Ethernet connection between the two devices for the ultimate in network isolation and audio performance.

The **Diretta Host** will connect to your main network (for Roon Core, etc.) and will also act as a gateway for the Target. The **Diretta Target** will connect only to the Host and your USB DAC or DDC.

## An Introduction to the Reference Roon Architecture

Welcome to the definitive guide for building a state-of-the-art Roon streaming endpoint. Before diving into the step-by-step instructions, it's important to understand the "why" behind this project. This introduction will explain the problem this architecture solves, why it's fundamentally superior to many high-cost commercial alternatives, and how this DIY project represents a direct and rewarding path to unlocking the ultimate sound quality from your Roon system.

### The Roon Paradox: A Powerful Experience with a Sonic Caveat

Roon is celebrated, almost universally, as the most powerful and engaging music management system available. Its rich metadata and seamless user experience are second to none. However, this functional supremacy has long been dogged by a persistent critique from a vocal segment of the audiophile community: that Roon's sound quality can be compromised, often described as "flat, dull, and lifeless" compared to other players.

This "Roon Sound" isn't a myth, nor is it a flaw in Roon's bit-perfect software. It is a potential symptom of Roon's powerful and resource-intensive nature. Roon's "heavyweight" Core requires significant processing power, which in turn generates electrical noise (RFI/EMI). When the computer running the Roon Core is in close proximity to your sensitive Digital-to-Analog Converter (DAC), this noise can contaminate the analog output stage, masking detail, shrinking the soundstage, and robbing the music of its vitality.

---

### Moving Beyond "Band-Aids" to a Foundational Solution

Roon Labs itself advocates for a "two-box" architecture to solve this primary issue: separating the demanding **Roon Core** from a lightweight network **Endpoint** (also called a streaming transport). This is the correct first step, as it offloads the heavy processing to a remote machine, isolating its noise from your audio rack.

However, even in this superior two-tier design, a more subtle problem remains. Standard network protocols, including Roon's own RAAT, deliver audio data in intermittent "bursts". This forces the endpoint's CPU to constantly spike its activity to process these bursts, causing rapid fluctuations in current draw. These fluctuations generate their own low-frequency electrical noise right at the endpoint—the component closest to your DAC.

High-end audio manufacturers attempt to combat the *symptoms* of this bursty traffic with various "Band-Aid" solutions: massive linear power supplies to better handle the current spikes, ultra-low-power CPUs to minimize the spikes' intensity, and extra filtering stages to clean up the resulting noise. While these strategies can help, they don't address the root cause of the noise: the bursty processing itself.

This guide presents a more elegant and dramatically more effective solution. Instead of trying to clean up the noise, we will build an architecture that prevents the noise from being generated in the first place.

---

### The Three-Tier Architecture: Roon + Diretta

This project evolves Roon's recommended two-box setup into an ultimate, three-tier system that provides multiple, compounding layers of isolation.

1.  **Tier 1: Roon Core**: Your powerful Roon server runs on a dedicated machine, placed far away from your listening room. It does all the heavy lifting, and its electrical noise is kept isolated from your audio system.
2.  **Tier 2: Diretta Host**: The first Raspberry Pi in our build acts as the **Diretta Host**. It connects to your main network, receives the audio stream from the Roon Core, and then prepares to forward it using a specialized protocol.
3.  **Tier 3: Diretta Target**: The second Raspberry Pi, the **Diretta Target**, connects *only* to the Host Pi via a short Ethernet cable, creating a point-to-point, galvanically isolated link. It receives the audio from the Host and connects to your DAC or DDC via USB.

### What Diretta and Audiolinux Bring to the Table

This design's superiority comes from two key software components running on the Raspberry Pi devices:

* **Audiolinux**: This is a purpose-built, real-time operating system designed specifically for audiophile use. Unlike a general-purpose OS, it's optimized to minimize processor latencies and system "jitter," providing a stable, low-noise foundation for our endpoint.
* **Diretta**: This groundbreaking protocol is the secret sauce that solves the root problem. It recognizes that fluctuations in the endpoint's processing load generate low-frequency electrical noise that can evade a DAC's internal filtering (as defined by its Power Supply Rejection Ratio, or PSRR) and subtly degrade its analog performance. To combat this, Diretta employs its "Host-Target" model, where the Host sends data in a continuous, synchronized stream of small, evenly spaced packets. This "averages" the processing load on the Target device, stabilizing its current draw and minimizing the generation of this pernicious electrical noise.

The combination of the physical galvanic isolation from the point-to-point Ethernet link and the processing noise elimination from the Diretta protocol creates a profoundly clean signal path to your DAC—one that can leapfrog solutions costing many thousands of dollars.

---

### A Rewarding Path to Sonic Excellence

This project is more than just a technical exercise; it's a rewarding way to engage with the hobby and take direct control over your system's performance. By building this "Diretta Bridge," you are not just assembling components; you are implementing a state-of-the-art architecture that addresses the core challenges of digital audio head-on. You will gain a deeper understanding of what truly matters for digital playback and be rewarded with a level of clarity, detail, and musical realism from Roon that you may not have thought possible.

Now, let's get started.

---

If you are located in the US, expect to pay around $365 in total (plus tax and shipping) to complete this build (prices subject to change):
- Hardware ($178)
- One year Audiolinux subscription ($69)
- Diretta Target license (€100)

## Table of Contents
1.  [Prerequisites](#1-prerequisites)
2.  [Initial Image Preparation](#2-initial-image-preparation)
3.  [Core System Configuration (Perform on Both Devices)](#3-core-system-configuration-perform-on-both-devices)
4.  [System Updates (Perform on Both Devices)](#4-system-updates-perform-on-both-devices)
5.  [Point-to-Point Network Configuration](#5-point-to-point-network-configuration)
6.  [Convenient & Secure SSH Access](#6-convenient--secure-ssh-access)
7.  [Clean the Boot Filesystem](#7-clean-the-boot-filesystem)
8.  [Diretta Software Installation & Configuration](#8-diretta-software-installation--configuration)
9.  [Final Steps & Roon Integration](#9-final-steps--roon-integration)
10. [Appendix 1: Optional IR Remote Control Setup](#10-appendix-1-optional-ir-remote-control-setup)
11. [Appendix 2: Argon ONE Fan Control](#11-appendix-2-argon-one-fan-control)
12. [Appendix 3: Purist Mode](#12-appendix-3-purist-mode)
13. [Appendix 4: Purist Mode Web UI Setup](#13-appendix-4-purist-mode-web-ui-setup)

---

### **How to Use This Guide**

This guide is designed to be as straightforward as possible, minimizing the need for manual file editing. The primary workflow will be to **copy and paste** command blocks from this document directly into a terminal window connected to your Raspberry Pi devices.

Here's the process you'll follow for most of the steps:

1.  **Connect via SSH**: You will use an SSH client on your main computer to log in to either the **Diretta Host** or the **Diretta Target** as instructed in each section.
2.  **Copy the Command**: In your web browser, hover over the top-right corner of a command block in this guide. A **copy icon** will appear. Click it to copy the entire block to your clipboard.
3.  **Paste and Execute**: Paste the copied commands into the correct SSH terminal window and press `Enter`.

The scripts and commands have been carefully written to be safe and to prevent errors, even if run more than once. By following this copy-and-paste method, you can avoid common typos and configuration mistakes.

---

### 1. Prerequisites

#### Hardware

A complete bill of materials is provided below. While other parts can be substituted, using these specific components improves the chances of a successful build.

**Core Components (from [pishop.us](https://www.pishop.us/) or similar supplier):**
* 2 x [Raspberry Pi 4 Model B/4GB](https://www.pishop.us/product/raspberry-pi-4-model-b-4gb/)
* 2 x Aluminum Heatsink for Raspberry Pi 4B (3-Pack) (check the box to add heatsinks on the RPi 4 product page)
* 2 x [Raspberry Pi 4 Case, Red/White](https://www.pishop.us/product/raspberry-pi-4-case-red-white/)
* 2 x [MicroSD Card Extreme Pro - 32 GB](https://www.pishop.us/product/microsd-card-extreme-pro-32-gb-class-10-blank/)
* 2 x [Raspberry Pi 45W USB-C Power Supply - White](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Required Networking Components:**
* 1 x [Plugable USB3 to Ethernet Adapter](https://www.amazon.com/dp/B00AQM8586) (for the Diretta Host)
* 1 x [Short CAT6 Ethernet Patch Cable](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (for the point-to-point link)

**Optional, but helpful for troubleshooting:**
* 1 x [Micro-HDMI to Standard HDMI (A/M), 2m Cable, White](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Raspberry Pi Official Keyboard - Red/White](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Optional Upgrades:**
* 2 x [Argon ONE V2 Aluminum Case for Raspberry Pi 4](https://www.amazon.com/Argon-Raspberry-Aluminum-Heatsink-Supports/dp/B07WP8WC3V/) (skip the aluminum heatsinks and official cases above)
* 1 x [Argon IR Remote](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (to add remote control capabilities to the Diretta Host)
* 1 x [FLIRC USB Universal Remote Control Receiver](https://flirc.tv/products/flirc-usb-receiver?variant=43513067569384) (needed to use the Argon IR Remote with a non-Argon ONE case)
* 1 x [AudioQuest Forest Ethernet Cable 0.75 M](https://www.amazon.com/AudioQuest-RJ-Forest-Ethernet-0-75m/dp/B0073H82U8/) (arrows pointing away from Diretta Host and towards the Diretta Target)
* 1 x [iFi LAN iSilencer](https://www.amazon.com/iFi-LAN-iSilencer-Electrical-Ethernet/dp/B0BV72SW8V/) (LAN filtering for the Diretta Target)
* 1 x [iFi Audio iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (to provide clean power to the Diretta Target)

**Required Audio Component:**
* 1 x USB DAC or DDC

**Required Build Tools:**
* Laptop or desktop PC running Linux, macOS, or Microsoft Windows with [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* An SD or microSD card reader
* An HDMI TV or display (optional, but useful for troubleshooting)

#### Software & Licensing Costs

* **Audiolinux:** An "Unlimited" license is recommended for enthusiasts, is currently **$139** (prices subject to change). However, it's fine to get started with a one year subscription, currently **$69**. Both options allow for installation on multiple devices within the same location.
* **Diretta Target:** A license is required for the Diretta Target device and currently costs **€100**.
    * **CRITICAL:** This license is locked to the specific hardware of the Raspberry Pi it is purchased for. It is essential that you perform the final licensing step on the exact hardware you intend to use permanently.
    * Diretta may offer a one-time replacement license for hardware failure within the first two years (please verify terms at time of purchase). If you change the hardware for any other reason, a new license must be purchased.

---

### 2. Initial Image Preparation

1.  **Purchase and Download:** Obtain the Audiolinux image from the [official website](https://www.audio-linux.com/). You will receive a link to download the `.img.gz` file via email typically within 24 hours of purchase.
2.  **Flash the Image:** Use your preferred imaging tool (e.g., [balenaEtcher](https://etcher.balena.io/) or
[Raspberry Pi Imager](https://www.raspberrypi.com/software/)) to write the downloaded Audiolinux image to **both** microSD cards.
    > **Note:** The Audiolinux image is a direct disk dump, not a compressed installer. As a result, the image file is quite large, and the flashing process can be unusually long. Expect it to take up to 15 minutes per card, depending on the speed of your microSD card and reader.

---

### 3. Core System Configuration (Perform on Both Devices)

After flashing, you must configure each Raspberry Pi individually to avoid network conflicts.

> **CRITICAL WARNING:** Because both devices are flashed from the exact same image, they will have identical `machine-id` values. If you power both devices on at the same time while connected to the same LAN, your DHCP server will likely assign them the same IP address, causing a network conflict.
>
> **You must perform the initial boot and configuration for each device one at a time.**

1.  Insert the microSD card into the **first** Raspberry Pi, connect it to your network, and power it on.
2.  Complete **all of Section 3** for this first device.
3.  Once the first device has rebooted with its new unique configuration, power it down.
4.  Now, power on the **second** Raspberry Pi and repeat **all of Section 3** for it.

The default SSH user is `audiolinux` with password `audiolinux`.
The default sudo/root password is `audiolinux0`.

You'll use the SSH client on your local computer to login to the RPi computers throughout this process. This client requires you to have a way to find the IP address of the RPi computers, which may change from one reboot to the next. The easiest way to get this information is from your home network router's web UI or app, but you can optionally install the [fing](https://www.fing.com/app/) app on your smartphone or tablet.

Once you have the IP address of one of your RPi computers, use the SSH client on your local computer to login using this process. Make note of the example `ssh` command since you'll use commands similar to this throughout this guide.
```bash
read -p "Enter the address of your RPi and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
echo '// Reminder: the password is audiolinux'
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
```

#### 3.1. Regenerate the Machine ID

The `machine-id` is a unique identifier for the OS installation. It **must** be different for each device. When asked for the root password below, enter `audiolinux0`

```bash
echo ""
echo "Old Machine ID: $(cat /etc/machine-id)"
echo "Enter the root password (audiolinux0) to regenerate the machine ID..."
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "New Machine ID: $(cat /etc/machine-id)"
```

#### 3.2. Set Unique Hostnames

Set a clear hostname for each device to easily identify them.

```bash
# On the Diretta Host
sudo hostnamectl set-hostname diretta-host
```

```bash
# On the Diretta Target
sudo hostnamectl set-hostname diretta-target
```

**At this point, shutdown the device. Repeat the [above steps](#3-core-system-configuration-perform-on-both-devices) for the second Raspberry Pi.**
```bash
sudo poweroff
```

---

### 4. System Updates (Perform on Both Devices)

For the steps in this section, it's usually most efficient (and least confusing) to complete all of Section 4 on the Diretta Host and then repeat the entire section on the Diretta Target.

Each RPi has its own machine ID, so you may power them up now. If you have two network cables, it's more
convenient to connect both of them to your home network at the same time for the next few steps, but you can
proceed one-at-a-time otherwise. **Note**: your router will likely assign them different IP addresses from the one you used to login initially. Be sure to use the new IP address with your SSH commands. Here's a reminder:

```bash
read -p "Enter the (new) address of your RPi and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
echo '// Reminder: the password is audiolinux'
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
```

#### 4.1. Install "Chrony" to update the system clock

The system clock has to be accurate before we can install updates. The Raspberry Pi has no NVRAM battery, so the clock must be set each time it boots. This is typically done by connecting to a network service. This script will make sure that the clock is set and stays correct during the operation of the computer.

```bash
echo '// Reminder: the root password is audiolinux0'
sudo id
curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Set your Timezone

```bash
clear
echo "Welcome to the interactive timezone setup."
echo "You will first select a region, then a specific timezone."

# Allow the user to select a region
PS3="
Please select a number for your region: "
select region in $(timedatectl list-timezones | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "You have selected the region: $region"
    break
  else
    echo "Invalid selection. Please try again."
  fi
done

echo ""

# Allow the user to select a timezone within that region
PS3="
Please select a number for your timezone: "
select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "You have selected the timezone: $timezone"
    break
  else
    echo "Invalid selection. Please try again."
  fi
done

# Set the selected timezone
echo
echo "Setting timezone to ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ Timezone has been set."

# Verify the change
echo
echo "Current system time and timezone:"
timedatectl status
```

#### 4.3. Workaround for Pacman Update Issue

A [known issue](https://archlinux.org/news/linux-firmware-2025061312fe085f-5-upgrade-requires-manual-intervention/) can prevent the system from updating due to conflicting NVIDIA firmware files (even though the RPi doesn't use them). To progress with the system upgrade, first remove `linux-firmware`, then reinstall it as part of the upgrade:

```bash
sudo pacman -Rdd --noconfirm linux-firmware
sudo pacman -Syu --noconfirm linux-firmware
```

#### 4.4. Run System and Menu Updates

Use the Audiolinux menu system to perform all updates.

1.  Run `menu` in the terminal.
2.  Select **INSTALL/UPDATE menu**.
3.  On the next screen, select **UPDATE system** and let the process complete.
4.  After the system update finishes, select **Update menu** from the same screen to get the latest version of the Audiolinux scripts.
5.  Exit the menu system to get back to the terminal.

---

### 5. Point-to-Point Network Configuration

In this section, we will create the network configuration files that will activate the dedicated private link. To avoid needing a physical keyboard and monitor (console access), we will perform these steps while both devices are still connected to your main LAN and accessible via SSH.

If you just finished updating your Diretta Target, click [here](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target) to jump to the point-to-point network configuration steps for the Target.

#### 5.1. Pre-configure the Diretta Host

1.  **Create Network Files:**
    Create the following two files on the **Diretta Host**. The `end0.network` file sets the static IP for the future point-to-point link. The `enp.network` file ensures the USB Ethernet adapter continues to get an IP from your main LAN.

    *File: `/etc/systemd/network/end0.network`*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/network/end0.network
    [Match]
    Name=end0

    [Network]
    Address=172.20.0.1/24
    EOT
    ```

    *File: `/etc/systemd/network/enp.network`*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/network/enp.network
    [Match]
    Name=enp*

    [Network]
    DHCP=yes
    DNSSEC=no
    EOT
    ```

    **Important:** Remove the old en.network file if present:
    ```
    # Remove the old generic network file to prevent conflicts.
    sudo rm -fv /etc/systemd/network/en.network
    ```

    Add an /etc/hosts entry for the Diretta Target:
    ```
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Add an entry for the Diretta Target if it doesn't exist
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **Enable IP Forwarding:**
    ```bash
    # Enable it for the current session
    sudo sysctl -w net.ipv4.ip_forward=1

    # Make it permanent across reboots
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Configure Network Address Translation (NAT):**
    ```bash
    # Check if the NAT rule already exists before adding it
    if ! sudo iptables -t nat -C POSTROUTING -s 172.20.0.0/24 -o enp+ -j MASQUERADE 2>/dev/null; then
      echo "Adding NAT rule for IP forwarding..."
      sudo iptables -t nat -A POSTROUTING -s 172.20.0.0/24 -o enp+ -j MASQUERADE
    fi

    # Save the rule to make it permanent
    sudo iptables-save | sudo tee /etc/iptables/iptables.rules
    sudo systemctl enable iptables.service
    ```

4.  **Driver selection for the Plugable USB to Ethernet Adapter**

    The default USB driver does not support all of the features of the Plugable Ethernet adapter. To get reliable performance, we need to tell the kernel's device manager how to handle the device when it's plugged in:
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Fix the `update_motd.sh` script**

    The script that updates the login banner (`/etc/motd`) does not handle the case of two network interfaces correctly. This prevents the login screen from becoming cluttered with incorrect IP address information after reboots. The new script below addresses this issue.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Finally, power-off the Host:
    ```bash
    sudo poweroff
    ```

#### 5.2. Pre-configure the Diretta Target

**Note:** If you have not performed [step 4](#4-system-updates-perform-on-both-devices) on the Diretta Target, do that [now](#4-system-updates-perform-on-both-devices), then return here.

On the **Diretta Target**, create the `end0.network` file. This configures its static IP and tells it to use the Diretta Host as its gateway for all internet traffic.

*File: `/etc/systemd/network/end0.network`*
```bash
cat <<'EOT' | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=1.1.1.1
EOT
```

**Important:** Remove the old en.network file if present:
```bash
# Remove the old generic network file to prevent conflicts.
sudo rm -fv /etc/systemd/network/en.network
```

Add an /etc/hosts entry for the Diretta Host:
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Add an entry for the Diretta Host if it doesn't exist
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

#### 5.3. The Physical Connection Change

> **Warning:** Double-check the contents of the files you just created. A typo could make a device inaccessible after rebooting, requiring a console session or re-flashing the SD card to fix.

1.  Once you have verified the files, perform a clean shutdown of **both** devices:
    ```bash
    sudo sync; sudo poweroff
    ```
2.  Disconnect both devices from your main LAN switch/router.
3.  Connect the **onboard Ethernet port** of the Diretta Host directly to the **onboard Ethernet port** of the Diretta Target using a single Ethernet cable.
4.  Plug the **USB-to-Ethernet adapter** into one of the blue USB 3.0 ports on the Diretta Host computer
5.  Connect the **USB-to-Ethernet adapter** on the Diretta Host to your main LAN switch/router.
6.  Power on both devices.

Upon booting, they will automatically use the new network configurations. **Note:** the IP address of your Diretta Host will likely have changed because it is now connected to your home network via the USB-to-Ethernet adapter. You'll have to return to your router's web UI or the Fing app to find the new address, which should be stable at this point.

```bash
read -p "Enter the final address of your Diretta Host and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
echo '// Reminder: the password is audiolinux'
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
```

You should now be able to ping the Target from the Host:
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

Also, you should be able to login to the Target from the Host:
```
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

From the target, let's try ping a host on the Internet to verify that the connection is working:
```
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Convenient & Secure SSH Access

#### 6.1. The `ProxyJump` Requirement

Now that the network is configured, the **Diretta Target** is on an isolated network (`172.20.0.0/24`) and cannot be reached directly from your main LAN. The only way to access it is to "jump" through the **Diretta Host**.

The `ProxyJump` directive in your local SSH configuration is the standard and required method to achieve this.

1.  Run this command on your local computer (not on the Raspberry Pi). It will prompt you for the Diretta Host's IP address and then print the exact configuration block you need.
```bash
clear
# --- Interactive SSH Alias Setup Script ---

SSH_CONFIG_FILE="$HOME/.ssh/config"

# Ensure the .ssh directory exists with the correct permissions
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

# Ensure the config file exists
touch "$SSH_CONFIG_FILE"
chmod 600 "$SSH_CONFIG_FILE"

# Check if the 'diretta-host' alias already exists
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ SSH configuration for 'diretta-host' already exists. No changes made."
else
  # Prompt for the IP address since the config is missing
  read -p "Enter the LAN IP address of your Diretta Host and press [Enter]: " Diretta_Host_IP

  # Append the new configuration using a heredoc for clarity
  cat <<EOT >> "$SSH_CONFIG_FILE"

# --- Diretta Configuration (added by script) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    StrictHostKeyChecking accept-new
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    StrictHostKeyChecking accept-new
    User audiolinux
    ProxyJump diretta-host
EOT

  echo "✅ SSH configuration for 'diretta-host' and 'diretta-target' has been added."
fi
```

2.  **Verify the Connection:**

You should now be able to connect to both devices using the new aliases. Test the connection with the following commands:

**To login to the Diretta Host:**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Type `exit` to logout.

**To login to the Diretta Target:** _(you'll be prompted for the password twice)_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```

**Note:** You can use `ssh host` and `ssh target` for short.

#### 6.2. Recommended: Secure Authentication with SSH Keys

While you can use passwords over the proxied connection, the most secure and convenient method is public key authentication. This uses a passphrase-protected SSH key managed by an agent (`ssh-agent`), eliminating the need to re-enter your password for every connection.

**On your local computer:**

1.  **Create an SSH Key (if you don't have one):**
    It's best practice to use a modern algorithm like `ed25519`. When prompted, enter a strong, memorable passphrase.
    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Set up `keychain` (for Linux users):**
    `keychain` makes the `ssh-agent` persistent across logins. macOS handles this automatically.

    * **Install keychain (Ubuntu/Debian):**
        ```bash
        sudo apt update && sudo apt install keychain
        ```
    * **Configure your shell:** Add the following line to your `~/.bashrc` or `~/.profile` to start `keychain` when you open a terminal.
        ```bash
        eval `keychain --eval --quiet id_ed25519`
        ```
    * Reload your shell by opening a new terminal or running `source ~/.bashrc`.

3.  **Add your key to the agent:**
    You will be prompted for your key's passphrase one time.
    ```bash
    ssh-add ~/.ssh/id_ed25519
    ```
    *(macOS users may need to use `ssh-add -K ~/.ssh/id_ed25519` on older systems to store the passphrase in the system Keychain.)*

4.  **Copy your Public Key to the Devices:**
    The `ssh-copy-id` command automatically appends your public key to the `~/.ssh/authorized_keys` file on the remote machine. Because `ProxyJump` is already configured, this will work seamlessly for the Target.
    ```bash
    echo ""
    echo "You will be prompted for the audiolinux password here."
    ssh-copy-id diretta-host
    echo ""
    echo "You will be prompted for the password twice here (for the proxy and the target)."
    ssh-copy-id diretta-target
    ```

You can now SSH to both devices (`ssh diretta-host`, `ssh diretta-target`) without a password, securely authenticated by your SSH key.

---

### 7. Clean the Boot Filesystem
The default behavior for Arch Linux is to leave the /boot filesystem in an unclean state if the computer is not shutdown cleanly. This is usually safe, but I've found that it can create a race condition when bringing up our private network. That, and users are likely to unplug these devices without shutting them down first. To protect against these issues, we'll add a workaround script that keeps the /boot filesystem (which is only changed during software updates) clean.

Please perform these steps on _both_ the Diretta Host and Target computers.

#### 7.1. Create the Repair Script

This script is safe to run both automatically at boot and manually on a live system.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.2. Create the `systemd` Service File and enable the service
```bash
cat <<'EOT' | sudo tee /etc/systemd/system/boot-repair.service
[Unit]
Description=Check and repair /boot filesystem before other services
DefaultDependencies=no
Conflicts=shutdown.target
Before=local-fs.target network-pre.target shutdown.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/check-and-repair-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=local-fs.target
EOT
sudo systemctl daemon-reload
sudo systemctl enable boot-repair.service
```

#### 7.3. Verification After a Clean Reboot
Not critical, but to make sure this is working as expected, do a reboot test. **Note:** Reboot the Target  first, then the Host.
```bash
sudo sync && sudo reboot
```
After the system is back online, check the journal on each computer for the service's logs from that boot session.
```bash
journalctl -b -u boot-repair.service
```
The expected output should show that the check ran and found nothing to do:
```text
Jun 27 10:17:55 diretta-host boot_repair[287]: /boot is clean. No action needed.
Jun 27 10:17:55 diretta-host boot_repair[290]: Check/repair process complete.
Jun 27 10:17:55 diretta-host systemd[1]: Finished Check and repair /boot filesystem before other services.
```

If you see `-- No entries --`, try this:
```bash
sudo systemctl restart boot-repair.service
journalctl -b -u boot-repair.service
```

---

### 8. Diretta Software Installation & Configuration

#### 8.1. On the Diretta Target

1.  Connect your USB DAC to one of the black USB 2.0 ports on the **Diretta Target** and ensure the DAC is powered on.
2.  SSH to the Target: `ssh diretta-target`.
3.  Run `menu`.
4.  Select **AUDIO extra menu**.
5.  Select **DIRETTA target installation**. You will see the following menu:
    ```
    What do you want to do?

    1) Install/update
    2) Enable/Disable Diretta Target
    3) Configure Audio card
    4) License
    5) Exit

    ?
    ```
6.  You should perform these actions in sequence:
    * Choose **1) Install/update** to install the software.
    * Choose **2) Enable/Disable Diretta Target** and enable it.
    * Choose **3) Configure Audio card**. The system will list your available audio devices. Enter the card number corresponding to your USB DAC.
        ```
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * Choose **4) License**. The system will run for 6 minutes in trial mode. Follow the on-screen link and instructions to purchase and apply your full license. This requires the internet access we configured in step 5.


7.  **Minimize disk I/O on the Diretta Target:** (optional but recommended for optimal performance)
    * Change `#Storage=auto` to `Storage=volatile` in `/etc/systemd/journald.conf`
    ```bash
    sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
    ```

#### 8.2. On the Diretta Host

1.  SSH to the Host: `ssh diretta-host`.
2.  Run `menu`.
3.  Select **AUDIO extra menu**.
4.  Select **DIRETTA host installation/configuration**. You will see the following menu:
    ```
    What do you want to do?

    1) Install/update
    2) Enable/Disable Diretta daemon
    3) Set Ethernet interface
    4) Edit configuration
    5) Exit

    ?
    ```
5.  You should perform these actions in sequence:
    * Choose **1) Install/update** to install the software. *(Note: you may see `error: package 'lld' was not found. Don't worry, that will be corrected automatically by the installation)*
    * Choose **2) Enable/Disable Diretta daemon** and enable it.
    * Choose **3) Set Ethernet interface**. It is critical to select `end0`, the interface for the point-to-point link.
        ```
        ?3
        Your available Ethernet interfaces are: end0  enp1s0u1u2
        Please type the name of your preferred interface:
        end0
        ```
    * Choose **4) Edit configuration** only if you need to make advanced changes. The previous steps should be sufficient.

6.  **Minimize disk I/O on the Diretta Host:** (optional but recommended for optimal performance)
    * Change `#Storage=auto` to `Storage=volatile` in `/etc/systemd/journald.conf`
    ```bash
    sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
    ```

---

### 9. Final Steps & Roon Integration

1.  **Install Roon Bridge (on Host):** If you use Roon, perform the following steps on the **Diretta Host**:
    * Run `menu`.
    * Select **INSTALL/UPDATE menu**.
    * Select **INSTALL/UPDATE Roonbridge**.
    * The installation will proceed. The installation may take a minute or two.

2.  **Enable Roon Bridge (on the Host):**
    * Select **Audio menu** from the Main menu
    * Select **SHOW audio service**
    * If you don't see **roonbridge** under enabled services, select **ROONBRIDGE enable/disable**

3.  **Reboot Both Devices:** For a clean start, `sudo sync && sudo reboot` both the Target and Host, in that order.

4.  **Configure Roon:**
    * Open Roon on your control device.
    * Go to `Settings` -> `Audio`.
    * Under the "Diretta" section, you should see your device. The name will be based on your DAC.
    * Click `Enable`, give it a name, and you are ready to play music!

Your dedicated Diretta link is now fully configured for pristine, isolated audio playback.
**Note:** The "Limited" zone for Diretta Target testing will disappear from Roon after six minutes of playback.  This is normal. At that point, you'll need to purchase a license for the Diretta Target. Cost is currently 100 Euros and it can take up to 48 hours for activation to complete. Once you receive the activation email from the Diretta team, just reboot your Target computer to pick up the activation.

---

### 10. Appendix 1: Optional IR Remote Control Setup

This guide provides instructions for installing and configuring an IR remote to control Roon. The setup is divided into two parts.

  * **Part 1** covers the hardware-specific setup. You will choose **one** of the two appendices depending on whether you are using the Flirc USB receiver or the Argon One case's built-in receiver.
  * **Part 2** covers the software setup for the `roon-ir-remote` control script, which is identical for both hardware options.

**Note:** You will _only_ perform these steps on the Diretta Host. The Target should not be used for relaying IR remote control commands to Roon Server.

---

#### **Part 1: IR Receiver Hardware Setup**

*Follow the appendix for the hardware you are using.*

##### **Option 1: Flirc USB IR Receiver Setup**

1.  **Purchase and Program the Flirc Device:**
    You'll need the Flirc USB IR Receiver, which can be purchased from their website: [https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    The Flirc device must be programmed on a desktop computer using the Flirc GUI software.

      * Plug the Flirc into your desktop computer and open the Flirc GUI.
      * Go to `Controllers` and select `Full Keyboard`.
      * Program the keys needed for the script (e.g., KEY_UP, KEY_DOWN, KEY_ENTER, etc.) by clicking the key in the GUI and then pressing the corresponding button on your physical remote.
      * Once programmed, plug the Flirc into the **Diretta Host**.

2.  **Test the Flirc Device:**
    Verify that the Raspberry Pi recognizes the Flirc as a keyboard.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Select the "Flirc" device from the menu. When you press buttons on your remote, you should see keyboard events printed to the screen.

---

##### **Option 2: Argon One IR Remote Setup**

1.  **Enable the IR Receiver Hardware:**
    You must enable the hardware overlay for the Argon One case's IR receiver.

      * This command will safely add the required hardware overlay to your `/boot/config.txt` file, first checking to ensure it isn't added more than once.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # Add the IR overlay if it's not already there
        if ! grep -q -F "$IR_CONFIG" "$BOOT_CONFIG"; then
          echo "Enabling Argon One IR Receiver..."
          echo "$IR_CONFIG" | sudo tee -a "$BOOT_CONFIG" > /dev/null
        else
          echo "Argon One IR Receiver already enabled."
        fi
        ```
      * A reboot is required for the hardware change to take effect.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **Install IR Tools and Enable Protocols:**
    Install `ir-keytable` and enable all kernel protocols so it can decode signals from your remote.

    ```bash
    sudo pacman -S --noconfirm v4l-utils
    sudo ir-keytable -p all
    ```

3.  **Capture Button Scancodes:**
    Run the test tool to see the unique scancode for each remote button.

    ```bash
    sudo ir-keytable -t
    ```

    Press each button you want to use and note its scancode from the `MSC_SCAN` event output (e.g., `value ca`). Press `Ctrl+C` when done.

4.  **Create the Keymap File:**
    This file maps the scancodes to standard key names.

      * Create a new keymap file:
        ```bash
        cat <<'EOT' | sudo tee /etc/rc_keymaps/argon.toml
        # /etc/rc_keymaps/argon.toml
        [[protocols]]
        name = "argon_remote"
        protocol = "nec"
        [protocols.scancodes]
        0xca = "KEY_UP"
        0xd2 = "KEY_DOWN"
        0x99 = "KEY_LEFT"
        0xc1 = "KEY_RIGHT"
        0xce = "KEY_ENTER"
        0x90 = "KEY_ESC"
        0x80 = "KEY_VOLUMEUP"
        0x81 = "KEY_VOLUMEDOWN"
        0xcb = "KEY_MUTE"
        EOT
        ```
      * If the scan codes in the example file above don't match the ones you recorded, edit the file (`sudo nano /etc/rc_keymaps/argon.toml`) and change them to match.

5.  **Create a `systemd` Service to Load the Keymap:**
    This service will load your keymap automatically on boot.

    Create a new service file and enable the service:
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/system/ir-keymap.service
    [Unit]
    Description=Load custom IR keymap
    After=multi-user.target

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/bin/ir-keytable -c -p nec -w /etc/rc_keymaps/argon.toml

    [Install]
    WantedBy=multi-user.target
    EOT
    sudo systemctl enable --now ir-keymap.service
    ```

6.  **Test the Input Device:**
    Verify the system is receiving keyboard events from the IR remote.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Select the `gpio_ir_recv` device. When you press buttons on the remote, you should see the corresponding key events.
    Type `CTRL-C` when you are finished testing.

---

#### **Part 2: Control Script Software Setup**

*After setting up your hardware in Part 1, follow these steps to install and configure the Python control script.*

##### **Step 1: Add `audiolinux` to the `input` group**
This is needed so that the `audiolinux` account has access to events from the remote control receiver.
```bash
sudo usermod --append --groups input audiolinux
```
Logout and log back in for this change to take effect. You can verify with this command:
```bash
echo ""
echo ""
echo "Checking your group memberships:"
echo "\$ groups"
groups
echo ""
echo "Above, you should see:"
echo "audiolinux realtime video input audio wheel"
```

##### **Step 2: Install Python via pyenv**

Install `pyenv` and the latest stable version of Python.

```bash
# Install build dependencies
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Install pyenv
curl -fsSL https://pyenv.run | bash

# Configure shell for pyenv
cat <<'EOT'>> ~/.bashrc

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"
EOT

. ~/.bashrc

# Install and set latest Python version
PYVER=$(pyenv install --list | grep '  3[0-9.]*$' | tail -n 1)
pyenv install $PYVER
pyenv global $PYVER
```

**Note:** It's normal for the `Installing Python-3.13.5...` part to take ~10 minutes as it compiles Python from source. Don't give up! Feel free to relax to some beautiful music using your new Diretta zone in Roon while you wait. It should be available while Python is installing on the Host.

---

#### **Step 3: Prepare and Patch `roon-ir-remote` Software**

Clone the script repository and fetch a patch to correctly handle keycodes by name instead of by number.

```bash
cd
# Clone the repo if it doesn't exist, otherwise update it
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/smangels/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi

cd roon-ir-remote

# Download the patch
curl -L -o roon-ir-remote.patch https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/roon-ir-remote.patch

PATCH_FILE="roon-ir-remote.patch"

# Use `yes n` to automatically answer "no" to any interactive prompts.
# We check the exit code of the patch command.
if yes n | patch -p1 --dry-run --silent < "$PATCH_FILE" >/dev/null 2>&1; then
  echo "✅ Patch has not been applied. Applying now..."
  patch -p1 < "$PATCH_FILE"
else
  echo "⚠️ Patch has already been applied or conflicts exist. Skipping."
fi

cd
```

---

#### **Step 4: Create the Roon Environment Config File**

Configure the script with your Roon details. **Note:** The `event_mapping` codes must match the key names you defined in your hardware setup (`KEY_ENTER`, `KEY_VOLUMEUP`, etc.).

```bash
echo "Please enter the following configuration details:"
read -p "Enter your email address: " MY_EMAIL_ADDRESS
echo ""
echo "Enter the name of your Roon zone."
echo "IMPORTANT: This must match the zone name in the Roon app exactly (case-sensitive)."
read -p "Enter your Roon Zone name: " MY_ROON_ZONE

# Create the configuration file
cat <<EOT> roon-ir-remote/app_info.json
{
  "roon": {
    "app_info": {
      "extension_id": "com.smangels.roon-ir-remote",
      "display_name": "Roon IR Remote",
      "display_version": "1.0.0",
      "publisher": "smangels",
      "email": "${MY_EMAIL_ADDRESS}",
      "website": "https://github.com/smangels/roon-ir-remote"
    },
    "zone": {
      "name": "${MY_ROON_ZONE}"
    },
    "event_mapping": {
      "codes": {
        "play_pause": "KEY_ENTER",
        "stop": "KEY_ESC",
        "skip": "KEY_RIGHT",
        "prev": "KEY_LEFT",
        "vol_up": "KEY_VOLUMEUP",
        "vol_down": "KEY_VOLUMEDOWN",
        "mute": "KEY_MUTE"
      }
    }
  }
}
EOT
```

---

#### **Step 5: Prepare and Test `roon-ir-remote`**

Install the script's dependencies into a virtual environment and run it for the first time.

```bash
cd ~/roon-ir-remote
pyenv virtualenv roon-ir-remote
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

The first time you run the script, you must **authorize the extension in Roon** by going to `Settings` -> `Extensions`.

With music playing in your new Diretta Roon zone, point your IR remote control directly at the Diretta Host computer and press the Play/Pause button (may be the center button in the 5-way controller). Also try Next and Previous. If these are not working, check your terminal window for any error messages.  Once you are finished testing, type CTRL-C to exit.

---

#### **Step 6: Create a `systemd` Service**

Create a service to run the script automatically in the background.

```bash
cat <<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
After=network.target

[Service]
Type=simple
User=${LOGNAME}
Group=${LOGNAME}
WorkingDirectory=/home/${LOGNAME}/roon-ir-remote
ExecStart=/home/${LOGNAME}/.pyenv/versions/roon-ir-remote/bin/python /home/${LOGNAME}/roon-ir-remote/roon_remote.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOT

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Check the status
sudo systemctl status roon-ir-remote.service
```

---

#### **Step 7: Install `set-roon-zone` script**
Good to have a script that you can use to update the Roon zone name later if needed. Here's how to install it:
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

To use it, simply login to the Diretta Host computer and type:
```bash
set-roon-zone
```
Follow the prompts to enter the new name for your Roon Zone. You may have to enter the root password to make the changes take effect.

#### **Step 8: Profit! 📈**

Your IR remote should now control Roon. Enjoy!

---

### 11. Appendix 2: Argon ONE Fan Control
If you decided to use an Argon ONE case for your Raspberry Pi, the default installer script assumes you're running a Debian O/S. However Audiolinux is based on Arch Linux, so you'll have to follow these steps instead.

If you are using Argon ONE cases for both Diretta Host and Target, you'll need to perform these steps on both computers.

#### Step 1: Skip the `argon1.sh` script in the manual
The manual says to download the argon1.sh script from download.argon40.com and pipe it to `bash`. This won't work, so skip this step and follow the steps below instead.

#### Step 2: Configure your system:
These commands will enable the I2C interface and add the specific `dtoverlay`
for the Argon ONE case. The script first attempts to uncomment the `i2c_arm`
parameter if it's commented out and then adds the `argonone` overlay if it's
missing, preventing errors and duplicate entries.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"
ARGON_OVERLAY="dtoverlay=argonone"

# --- Enable I2C by uncommenting the line if it exists ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi

# --- Add the Argon One overlay if it's not already there ---
if ! grep -q -F "$ARGON_OVERLAY" "$BOOT_CONFIG"; then
  echo "Adding Argon One overlay..."
  echo "$ARGON_OVERLAY" | sudo tee -a "$BOOT_CONFIG" > /dev/null
else
  echo "Argon One overlay already present."
fi
```

#### Step 3: Configure `udev` permissions
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

#### Step 4: Install the Argon One Package
```bash
yay -S argonone-c-git
```

#### Step 5: Switch Argon ONE case from hardware to software control
```bash
sudo pacman -S --noconfirm --needed i2c-tools
# Create a systemd override file to switch the case to software mode on boot
sudo mkdir -pv /etc/systemd/system/argononed.service.d
printf '%s\n' \
  '[Service]' \
  'ExecStartPre=/usr/bin/i2cset -y 1 0x1a 0' \
  | sudo tee /etc/systemd/system/argononed.service.d/software-mode.conf > /dev/null
```

#### Step 6: Enable the Service
```bash
# Reload the systemd manager to read the new configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable argononed.service
```

#### Step 7: Reboot
Finally, reboot your Raspberry Pi for all changes to take effect (Target first, then Host):
```bash
sudo sync && sudo reboot
```

Now, the fan will be controlled by the daemon, and the power button will have full functionality.

#### Step 8: Verify the service
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

#### Step 9: Review Fan Mode and Settings:
To see the current configuration values, run the following command:
```bash
sudo argonone-cli --decode
```

To adjust those values, you must create a config file. Use these values to start:
```bash
cat <<'EOT' | sudo tee /etc/argononed.conf
[Schedule]
temp0=55
fan0=0
temp1=60
fan1=50
temp2=65
fan2=100

[Setting]
hysteresis=3
EOT
```

Restart the service to pick up the new configuration values:
```bash
sudo systemctl restart argononed.service
echo ""
echo "Updated fan values:"
sudo argonone-cli --decode
```

Now, feel free to adjust the values as needed, following the steps above.

### 12. Appendix 3: Purist Mode
There is minimal network and background activity on the Diretta Target computer that is not related to music playback using the Diretta protocol. However, some users prefer to take extra steps to reduce the possibility of such activity. We are already on the extreme edge of audio performance, so why not?

---
> CRITICAL WARNING: For the Diretta Target ONLY
>
> The `purist-mode` script and all instructions in this appendix are designed exclusively for the Diretta Target.
> 
> Do NOT install or run this script on the Diretta Host. Doing so will drop the Host's connection to your main network, making it unreachable and unable to communicate with your Roon Core or streaming services. This would render the entire system inoperable until you can gain console access (with a physical keyboard and monitor) to revert the changes.
---

#### Step 1: Install the `purist-mode` script **(only on the Diretta Target computer)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode
```

To run it, simply login to the Diretta Target and type `purist-mode`:
```bash
purist-mode
```

For example:
```text
[audiolinux@diretta-target ~]$ purist-mode
This script requires sudo privileges. You may be prompted for a password.
(Note: The default sudo password for Audiolinux is 'audiolinux0')
[sudo] password for root:
🚀 Activating Purist Mode...
  -> Stopping time synchronization service (chronyd)...
  -> Stopping Argon One daemon (argononed.service)...
  -> Disabling DNS lookups...
     Backup of /etc/nsswitch.conf created.
     DNS lookups disabled (set to local-only resolution).
  -> Dropping default gateway...
     Default gateway removed.

✅ Purist Mode is ACTIVE.
   To restore normal operation, run: purist-mode --revert
```

Listen for a while to see if you prefer the sound (or peace of mind).

#### Step 2: Enable Purist Mode by Default

If you've decided that you prefer the sound with Purist Mode enabled, make it the default after each reboot.

```bash
echo ""
echo "- Disabling Purist Mode to ensure a clean state"
purist-mode --revert

echo ""
echo "- Creating the Service to Revert to Standard Mode on Every Boot"
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-revert-on-boot.service
[Unit]
Description=Revert Purist Mode on Boot to Ensure Standard Operation
After=network-online.target
Wants=network-online.target
Before=purist-mode-auto.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/purist-mode --revert

[Install]
WantedBy=multi-user.target
EOT

echo ""
echo "- Creating the Delayed Auto-Activation Service"
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-auto.service
[Unit]
Description=Activate Purist Mode 60 seconds after boot

[Service]
Type=oneshot
ExecStart=/bin/bash -c "sleep 60 && /usr/local/bin/purist-mode"

[Install]
WantedBy=multi-user.target
EOT

echo ""
echo "- Enabling the new services"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
```

#### Step 3: Install a wrapper around the `menu` command
Many functions in the Audiolinux require Internet access. To keep things working as expected, add a wrapper around the `menu` command that disables Purist mode while you are using the menu, enabling it again when you exit to the terminal.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Add a wrapper around the menu command"
  cat <<'EOT' | tee -a ~/.bashrc

# Custom wrapper for the Audiolinux menu to manage Purist Mode
menu_wrapper() {
    local was_active=false
    # Check the initial state of Purist Mode by looking for the backup file.
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        was_active=true
    fi

    # If Purist Mode was active, temporarily revert it for the menu.
    if [ "$was_active" = true ]; then
        echo "Checking credentials to manage Purist Mode..."
        echo "(Note: The default sudo password for Audiolinux is 'audiolinux0')"
        sudo -v

        echo "Temporarily disabling Purist Mode to run menu..."
        purist-mode --revert > /dev/null 2>&1 # Revert quietly
    fi

    # Call the original menu command
    /usr/bin/menu

    # If Purist Mode was active before, re-enable it now.
    if [ "$was_active" = true ]; then
        echo "Re-activating Purist Mode..."
        purist-mode > /dev/null 2>&1 # Activate quietly
        echo "Purist Mode is active again."
    fi
}

# Alias the 'menu' command to our new wrapper function
alias menu='menu_wrapper'
# Aliases to manage the automatic Purist Mode service
alias purist-mode-auto-enable='echo "Enabling Purist Mode on boot..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Disabling Purist Mode on boot..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

#### Understanding the Purist Mode States

The Purist Mode system is designed to be flexible, allowing you to control it manually or have it activate automatically after the system boots. It operates in two primary states:

  * **Disabled (Standard Mode):**
    This is the normal, fully functional state of the Diretta Target. The network gateway is active, all services (`chronyd`, `argononed`) are running, and the device operates without restrictions.

  * **Active (Purist Mode):**
    This is the optimized state for critical listening. The network gateway is dropped to prevent internet traffic, and non-essential background services (including the Argon ONE fan) are stopped to minimize all potential system interference.

These states are managed in two ways: **automatically** on boot and **manually** via the command line.

##### Automatic Control (On Boot)

The boot-up process is designed to be safe and predictable, with an optional automated switch to Purist Mode.

1.  **Mandatory Revert on Boot:** Regardless of the state it was in when shut down, the Diretta Target **always** boots into **Standard Mode** first. This is a critical feature that ensures essential services like network time synchronization can run correctly.

2.  **Optional Auto-Activation:** If you have enabled the automatic feature, the system will wait 60 seconds after booting and then automatically switch to **Purist Mode**. This provides a "set it and forget it" experience for users who always prefer listening in the optimized state.

##### Manual Control (Interactive Use)

You have full interactive control over the system at any time.

  * To **manually activate** Purist Mode for a listening session, login to the Diretta Target computer and run:

    ```bash
    purist-mode
    ```

  * To **manually disable** Purist Mode and return to standard operation, run:

    ```bash
    purist-mode --revert
    ```

  * To control the **automatic boot behavior**, use the convenience aliases on the Diretta Target:

    ```bash
    # This enables the 60-second auto-activation on the next boot
    purist-mode-auto-enable

    # This disables the auto-activation on the next boot
    purist-mode-auto-disable
    ```

---

### 13. Appendix 4: Purist Mode Web UI Setup

This appendix provides instructions for installing a simple web-based application on the **Diretta Host**. This application provides an easy-to-use interface, accessible from a phone or tablet, to control Purist Mode on the **Diretta Target** without needing to use the command line.

> **CRITICAL WARNING: Perform these steps carefully.**
> This setup involves creating a new user and modifying security settings. Follow the instructions precisely to ensure the system remains secure and functional.

The setup is divided into two parts: first, we configure the **Diretta Target** to securely accept commands, and second, we install the web application on the **Diretta Host**.

---

#### **Part 1: Diretta Target Configuration**

On the **Diretta Target**, we will create a new, non-interactive user with very limited permissions. This user will only be allowed to run the specific commands needed to manage Purist Mode.

1.  **SSH to the Diretta Target:**
    ```bash
    ssh diretta-target
    ```

2.  **Create a New User for the App:**
    This command creates a new user named `purist-app` that cannot be used for interactive logins.
    ```bash
    sudo useradd --system --create-home --shell /usr/bin/nologin purist-app
    ```

3.  **Create Secure Command Scripts:**
    We will create three small, dedicated scripts that are the *only* actions the web app is allowed to perform. This is a critical security step.
    ```bash
    # Script to get the current status
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        IS_ACTIVE="true"
    fi
    if systemctl is-enabled --quiet purist-mode-auto.service; then
        IS_AUTO_ENABLED="true"
    fi
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED}"
    EOT

    # Script to toggle Purist Mode
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    #!/bin/bash
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        /usr/local/bin/purist-mode --revert
    else
        /usr/local/bin/purist-mode
    fi
    EOT

    # Script to toggle the auto-start service
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
        systemctl disable --now purist-mode-auto.service
    else
        systemctl enable purist-mode-auto.service
    fi
    EOT

    # Make the new scripts executable
    sudo chmod +x /usr/local/bin/pm-*
    ```

4.  **Grant Sudo Permissions:**
    This step allows the `purist-app` user to run our three new scripts with root privileges, without needing a password.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # Allow the purist-app user to run the specific control scripts
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    EOT
    ```

---

#### **Part 2: Diretta Host Configuration**

Now, on the **Diretta Host**, we will generate the SSH key, install the web application, and set it up to run as a service.

1.  **SSH to the Diretta Host:**
    ```bash
    ssh diretta-host
    ```

2.  **Generate a Dedicated SSH Key:**
    This creates a new SSH key pair specifically for the web app. It will have no passphrase.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Authorize the Key on the Target:**
    This step will securely copy the public key to the Target and configure it with the necessary security restrictions, all in one command.
    ```
		echo "--- Authorizing the new SSH key on the Diretta Target ---"

		# Step A: Copy the public key to the Target's home directory
		echo "--> Copying public key to the Target..."
		scp ~/.ssh/purist_app_key.pub diretta-target:

		# Step B: Run a script on the Target to set up the key for the 'purist-app' user
		echo "--> Running setup script on the Target..."
		ssh diretta-target <<'END_OF_REMOTE_SCRIPT'
		set -e
		# Read the public key from the file we just copied
		PUB_KEY=$(cat purist_app_key.pub)

		# Ensure the .ssh directory exists and has correct permissions
		sudo mkdir -p /home/purist-app/.ssh
		sudo chmod 0700 /home/purist-app/.ssh

		# Create the authorized_keys file with the required security restrictions
		echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

		# Set final ownership and permissions
		sudo chown -R purist-app:purist-app /home/purist-app/.ssh
		sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

		# Clean up the copied public key file
		rm purist_app_key.pub
		echo "--> Target setup complete."
		END_OF_REMOTE_SCRIPT

		echo "✅ SSH key has been successfully authorized on the Target."
    ```

4.  **Install Dependencies and Avahi:**
    Install Flask and the Avahi daemon for `.local` name resolution.
    ```bash
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm python-flask avahi

    # Dynamically find the USB Ethernet interface name (e.g., enp1s0u1u2)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/enp/{print $2}')

    # Create a configuration override for Avahi to isolate it to the USB interface
    echo "--- Configuring Avahi to use interface: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    EOT

    # Enable and start the Avahi daemon
    sudo systemctl enable --now avahi-daemon.service
    ```

5.  **Install the Flask App:**
    Create a directory for the app and download the Python script directly from GitHub.
    ```bash
    mkdir -p ~/purist-mode-webui
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

6.  **Create the `systemd` Service:**
    This service will run the web app automatically on boot.
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/system/purist-webui.service
    [Unit]
    Description=Purist Mode Web UI
    After=network-online.target

    [Service]
    Type=simple
    User=audiolinux
    Group=audiolinux
    WorkingDirectory=/home/audiolinux/purist-mode-webui
    ExecStart=/usr/bin/python app.py
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    EOT
    ```

7.  **Enable and Start the Web App:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now purist-webui.service
    ```

---

#### **Part 3: Access the Web UI**

You're all set! Open a web browser on your phone, tablet, or computer connected to the same network as the Diretta Host. Navigate to:

[http://diretta-host.local](http://diretta-host.local)

You should now see the control panel, allowing you to easily manage Purist Mode.

