# Building a Dedicated Diretta Link with AudioLinux on Raspberry Pi

This guide provides comprehensive, step-by-step instructions for configuring two Raspberry Pi devices as a dedicated Diretta Host and Diretta Target. This setup uses a direct, point-to-point Ethernet connection between the two devices for the ultimate in network isolation and audio performance.

The **Diretta Host** will connect to your main network (to access your music server) and will also act as a gateway for the Target. The **Diretta Target** will connect only to the Host and your USB DAC or DDC.

# Disclaimer

Diretta is a moving target. However, I'm pleased to confirm that version 146_7 (and later?) performs very well with a ~45% reduction in CPU usage on the Target, and it sounds great.

Here are some links for more information:
* https://help.diretta.link/support/solutions/articles/73000661018-146
* https://help.diretta.link/support/solutions/articles/73000661171-dds-diretta-direct-stream


## An Introduction to the Reference Roon Architecture

Welcome to the definitive guide for building a state-of-the-art Roon streaming endpoint. While AudioLinux supports other protocols, I will use Roon as the example for this build. You may use the menu system on the Diretta Host to install support for other protocols, including HQPlayer, Audirvana, DLNA, AirPlay, etc. Before diving into the step-by-step instructions, it's important to understand the "why" behind this project. This introduction will explain the problem this architecture solves, why it's fundamentally superior to many high-cost commercial alternatives, and how this DIY project represents a direct and rewarding path to unlocking the ultimate sound quality from your Roon system.

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

### What Diretta and AudioLinux Bring to the Table

This design's superiority comes from two key software components running on the Raspberry Pi devices:

* **AudioLinux**: This is a purpose-built, real-time operating system designed specifically for audiophile use. Unlike a general-purpose OS, it's optimized to minimize processor latencies and system "jitter," providing a stable, low-noise foundation for our endpoint.
* **Diretta**: This groundbreaking protocol is the secret sauce that solves the root problem. It recognizes that fluctuations in the endpoint's processing load generate low-frequency electrical noise that can evade a DAC's internal filtering (as defined by its Power Supply Rejection Ratio, or PSRR) and subtly degrade its analog performance. To combat this, Diretta employs its "Host-Target" model, where the Host sends data in a continuous, synchronized stream of small, evenly spaced packets. This "averages" the processing load on the Target device, stabilizing its current draw and minimizing the generation of this pernicious electrical noise.

The combination of the physical galvanic isolation from the point-to-point Ethernet link and the processing noise elimination from the Diretta protocol creates a profoundly clean signal path to your DAC—one that can leapfrog solutions costing many thousands of dollars.

---

### A Rewarding Path to Sonic Excellence

This project is more than just a technical exercise; it's a rewarding way to engage with the hobby and take direct control over your system's performance. By building this "Diretta Bridge," you are not just assembling components; you are implementing a state-of-the-art architecture that addresses the core challenges of digital audio head-on. You will gain a deeper understanding of what truly matters for digital playback and be rewarded with a level of clarity, detail, and musical realism from Roon that you may not have thought possible.

Now, let's get started.

---

If you are located in the US, expect to pay around $295 (plus tax and shipping) to complete the basic build, limited to 44.1 kHz playback (for evaluation), plus another €100 to enable hi-res playback (prices subject to change):
- Hardware ($225)
- One year AudioLinux subscription ($69)
- Diretta Target license (€100)

## Table of Contents
1.  [Prerequisites](#1-prerequisites)
2.  [Initial Image Preparation](#2-initial-image-preparation)
3.  [Core System Configuration (Perform on Both Devices)](#3-core-system-configuration-perform-on-both-devices)
4.  [System Updates (Perform on Both Devices)](#4-system-updates-perform-on-both-devices)
5.  [Point-to-Point Network Configuration](#5-point-to-point-network-configuration)
6.  [Convenient & Secure SSH Access](#6-convenient--secure-ssh-access)
7.  [Common System Optimizations](#7-common-system-optimizations)
8.  [Diretta Software Installation & Configuration](#8-diretta-software-installation--configuration)
9.  [Final Steps & Roon Integration](#9-final-steps--roon-integration)
10. [Appendix 1: Optional Argon ONE Fan Control](#10-appendix-1-optional-argon-one-fan-control)
11. [Appendix 2: Optional IR Remote Control](#11-appendix-2-optional-ir-remote-control)
12. [Appendix 3: Optional Purist Mode](#12-appendix-3-optional-purist-mode)
13. [Appendix 4: Optional System Control Web UI](#13-appendix-4-optional-system-control-web-ui)
14. [Appendix 5: System Health Checks](#14-appendix-5-system-health-checks)
15. [Appendix 6: Advanced Realtime Performance Tuning](#15-appendix-6-advanced-realtime-performance-tuning)
16. [Appendix 7: Optimize CPU with Event-Driven Hooks](#16-appendix-7-optimize-cpu-with-event-driven-hooks)
17. [Appendix 8: Optional Purist 100Mbps Network Mode](#17-appendix-8-optional-purist-100mbps-network-mode)

---

### **How to Use This Guide**

This guide is designed to be as straightforward as possible, minimizing the need for manual file editing. The primary workflow will be to **copy and paste** command blocks from this document directly into a terminal window connected to your Raspberry Pi devices.

Here's the process you'll follow for most of the steps:

1.  **Connect via SSH**: You will use an SSH client on your main computer to log in to either the **Diretta Host** or the **Diretta Target** as instructed in each section.
2.  **Copy the Command**: In your web browser, hover over the top-right corner of a command block in this guide. A **copy icon** will appear. Click it to copy the entire block to your clipboard.
3.  **Paste and Execute**: Paste the copied commands into the correct SSH terminal window and press `Enter`.

The scripts and commands have been carefully written to be safe and to prevent errors, even if run more than once. By following this copy-and-paste method, you can avoid common typos and configuration mistakes.

---

### Video Walkthrough

Here's a link to a series of short videos walking through this process:

* [Diretta Build Walkthrough with Two Raspberry Pi Computers](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Prerequisites

#### Hardware

A complete bill of materials is provided below. While other parts can be substituted, using these specific components improves the chances of a successful build.

**Core Components (from [pishop.us](https://www.pishop.us/) or similar supplier):**
* 1 x [Raspberry Pi 4 Model B/4GB](https://www.pishop.us/product/raspberry-pi-4-model-b-4gb/) (for the Diretta Host)
* 1 x [Flirc Raspberry Pi 4 Case](https://www.pishop.us/product/flirc-raspberry-pi-4-case/)
* 1 x [Raspberry Pi 5/2GB](https://www.pishop.us/product/raspberry-pi-5-2gb/) (for the Diretta Target)
* 1 x [Flirc Raspberry Pi 5 Case](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [MicroSD Card Extreme Pro - 32 GB](https://www.pishop.us/product/microsd-card-extreme-pro-32-gb-class-10-blank/)
* 2 x [Raspberry Pi 45W USB-C Power Supply - White](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Required Networking Components:**
* 1 x [Plugable USB3 to Ethernet Adapter](https://www.amazon.com/dp/B00AQM8586) (for the Diretta Host)
* 1 x [Short CAT6 Ethernet Patch Cable](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (for the point-to-point link)

**Optional, but helpful for troubleshooting:**
* 1 x [Micro-HDMI to Standard HDMI (A/M), 2m Cable, White](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Raspberry Pi Official Keyboard - Red/White](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Optional Upgrades:**
* 1 x [Argon ONE V2 Aluminum Case for Raspberry Pi 4](https://www.amazon.com/Argon-Raspberry-Aluminum-Heatsink-Supports/dp/B07WP8WC3V/) (instead of the Flirc case)
* 1 x [Argon ONE V3 Raspberry Pi 5 Case](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (instead of the Flirc case)
* 1 x [Argon IR Remote](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (to add remote control capabilities to the Diretta Host)
* 1 x [Flirc USB IR Receiver](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (to use the Argon IR Remote with the Diretta Host in a Flirc Case)
* 1 x [Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (for the point-to-point connection between Host and Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (to provide clean power to the Diretta Target)
* 1 x [iFi SilentPower Pulsar USB Cable](https://www.silentpower.tech/products/pulsar-usb) (USB connection with galvanic isolation)
* 1 x [DC 5.5mm x 2.1mm to UsB C Adapter](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (needed to adapt the plug on the iPower Elite to the Diretta Target's USB C power input)
* 1 x [SMSL PO100 PRO DDC](https://www.amazon.com/dp/B0BLYVZCV5) (a digital-to-digital converter for DACs that lack a good USB input implementation)
* 1 x [USB Wireless Adapter](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (a wired connection is highly preferable and more reliable, but if adding wired Ethernet near your audio system is impractical, replace the Plugable USB to Ethernet adapter with this Wi-Fi adapter)
* 1 x [Power Splitter Cord](https://www.amazon.com/dp/B01K3ADXX2?th=1) (plug both 45W power adapters into a single receptacle)

**Required Audio Component:**
* 1 x USB DAC or DDC

**Required Build Tools:**
* Laptop or desktop PC running Linux, macOS (iTerm2, https://iterm2.com/, recommended), or Microsoft Windows with [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* An SD or microSD card reader
* An HDMI TV or display (optional, but useful for troubleshooting)

#### Software & Licensing Costs

* **AudioLinux:** An "Unlimited" license is recommended for enthusiasts, is currently **$139** (prices subject to change). However, it's fine to get started with a one year subscription, currently **$69**. Both options allow for installation on multiple devices within the same location.
* **Diretta Target:** A license is required for high-res playback (greater than 44.1 kHz PCM) via the Diretta Target device and currently costs **€100**.
    * You may evaluate the Diretta Target using 44.1 kHz streams for an extended period of time. Therefore, I recommend using Roon's **Sample rate conversion** feature under **MUSE** DSP settings to convert all content to 44.1 kHz during your evaluation period. Once you are satisfied, purchase the Diretta Target license to remove the restriction. Leave sample rate conversion settings engaged until you receive the second email from the Diretta team indicating that your hardware has been activated.
    * **CRITICAL:** This license is locked to the specific hardware of the Raspberry Pi it is purchased for. It is essential that you perform the final licensing step on the exact hardware you intend to use permanently.
    * Diretta may offer a one-time replacement license for hardware failure within the first two years (please verify terms at time of purchase). If you change the hardware for any other reason, a new license must be purchased.

---

### 2. Initial Image Preparation

1.  **Purchase and Download:** Obtain the AudioLinux image from the [official website](https://www.audio-linux.com/). You will receive a link to download the `.img.gz` file via email typically within 24 hours of purchase.
2.  **Flash the Image:** Use your preferred imaging tool (e.g., [balenaEtcher](https://etcher.balena.io/) or
[Raspberry Pi Imager](https://www.raspberrypi.com/software/)) to write the downloaded AudioLinux image to **both** microSD cards.
    > **Note:** The AudioLinux image is a direct disk dump, not a compressed installer. As a result, the image file is quite large, and the flashing process can be unusually long. Expect it to take up to 15 minutes per card, depending on the speed of your microSD card and reader.

---

### 3. Core System Configuration (Perform on Both Devices)

After flashing, you must configure each Raspberry Pi individually to avoid network conflicts.

For the best performance, this guide uses the more powerful Raspberry Pi 5 as the Diretta Target (the device connected to your DAC) and the Raspberry Pi 4 as the Diretta Host. You will configure the Host first.

**Note:** While this is the optimal configuration, great results are possible using RPi4 computers for both. However, using RPi5 for both Host and Target could create problems due to the RPi5's more aggressive use of Energy Efficient Ethernet (EEE) on its onboard network interface. Two RPi5s may result in flapping on the point-to-point link. And, since the Diretta protocol does not support retransmits when packets are lost, you may experience audio dropouts with a RPi5 to RPi5 configuration.

> **CRITICAL WARNING:** Because both devices are flashed from the exact same image, they will have identical `machine-id` values. If you power both devices on at the same time while connected to the same LAN, your DHCP server will likely assign them the same IP address, causing a network conflict.
>
> **You must perform the initial boot and configuration for each device one at a time.**

1.  Insert the microSD card into the **first** Raspberry Pi, connect it to your network, and power it on. **Note:** If you're using the Argon ONE case, you may hear audible noise from the fan. Don't worry. Once you've finished with Diretta setup, there are instructions in [Appendix 1](#10-appendix-1-optional-argon-one-fan-control) for addressing the fan noise.
2.  Complete **all of Section 3** for this first device.
3.  Once the first device has rebooted with its new unique configuration, power it down.
4.  Now, power on the **second** Raspberry Pi and repeat **all of Section 3** for it.

Please refer to the receipt from your Audiolinux purchase for the default SSH user and sudo/root passwords. Make a note of them as you will use them many times throughout this process.

You'll use the SSH client on your local computer to login to the RPi computers throughout this process. This client requires you to have a way to find the IP address of the RPi computers, which may change from one reboot to the next. The easiest way to get this information is from your home network router's web UI or app, but you can optionally install the [fing](https://www.fing.com/app/) app on your smartphone or tablet.

Once you have the IP address of one of your RPi computers, use the SSH client on your local computer to login using this process. Make note of the example `ssh` command since you'll use commands similar to this throughout this guide.
```bash
cmd=$(cat <<'EOT'
read -rp "Enter the address of your RPi and hit [enter]: " RPi_IP_Address
echo 'Reminder: the default password is in your AudioLinux email from Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Regenerate the Machine ID

The `machine-id` is a unique identifier for the OS installation. It **must** be different for each device.

```bash
echo ""
echo "Old Machine ID: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "New Machine ID: $(cat /etc/machine-id)"
```

#### 3.2. Set Unique Hostnames

Set a clear hostname for each device to easily identify them. **Note:** If this is not your first build using these instructions and you already have a Diretta Host/Target pair on your network, consider selecting a different name for this new Diretta Host, like `diretta-host2`, just for this part. Doing so will make it easier to access the two independently later.

**On your FIRST device (the future Diretta Host):**
```bash
# On the Diretta Host
sudo hostnamectl set-hostname diretta-host
```

**On your SECOND device (the future Diretta Target):**
```bash
# On the Diretta Target
sudo hostnamectl set-hostname diretta-target
```

**At this point, shutdown the device. Repeat the [above steps](#3-core-system-configuration-perform-on-both-devices) for the second Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. System Updates (Perform on Both Devices)

For the steps in this section, it's usually most efficient (and least confusing) to complete all of Section 4 on the Diretta Host and then repeat the entire section on the Diretta Target.

Each RPi has its own machine ID, so you may power them up now. If you have two network cables, it's more
convenient to connect both of them to your home network at the same time for the next few steps, but you can
proceed one-at-a-time otherwise. **Note**: your router will likely assign them different IP addresses from the one you used to login initially. Be sure to use the new IP address with your SSH commands. Here's a reminder:

```bash
cmd=$(cat <<'EOT'
read -rp "Enter the (new) address of your RPi and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. Install "Chrony" to update the system clock

The system clock has to be accurate before we can install updates. The Raspberry Pi has no NVRAM battery, so the clock must be set each time it boots. This is typically done by connecting to a network service. This script will make sure that the clock is set and stays correct during the operation of the computer.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Set your Timezone

```bash
cmd=$(cat <<'EOT'
clear
echo "Welcome to the interactive timezone setup."
echo "You will first select a region, then a specific timezone."

# Allow the user to select a region
PS3="
Please select a number for your region: "
select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
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
EOT
)
bash -c "$cmd"
```

#### 4.3. Install DNS Utils
Install the `dnsutils` package so that the **menu** update will have access to the `dig` command:
```bash
sudo pacman -S --noconfirm dnsutils
```

#### 4.4. Run System and Menu Updates

Use the AudioLinux menu system to perform all updates. Have your email from Piero with your image download user and password. You'll need these for the menu update. It will ask for **your menu update user**, which is a bit confusing. It's asking for the username and password that you used to download the AudioLinux install image.

1.  Run `menu` in the terminal.
2.  Select **INSTALL/UPDATE menu**.
3.  On the next screen, select **UPDATE system** and let the process complete.
4.  After the system update finishes, select **Update menu** from the same screen to get the latest version of the AudioLinux scripts.
5.  Exit the menu system to get back to the terminal.

---
> Note: Workaround for Pacman Update Issue
>
> There was a [known issue](https://archlinux.org/news/linux-firmware-2025061312fe085f-5-upgrade-requires-manual-intervention/) that could prevent the system from updating due to conflicting NVIDIA firmware files (even though the RPi doesn't use them). If you encounter this issue, to progress with the system upgrade, first remove `linux-firmware`, then reinstall it as part of the upgrade:
>
> ```bash
> sudo pacman -Rdd --noconfirm linux-firmware
> sudo pacman -Syu --noconfirm linux-firmware
> ```
---

#### 4.5. Reboot
Reboot to load the kernel and other updates:
```bash
sudo sync && sudo reboot
```

---

### 5. Point-to-Point Network Configuration

In this section, we will create the network configuration files that will activate the dedicated private link. To avoid needing a physical keyboard and monitor (console access), we will perform these steps while both devices are still connected to your main LAN and accessible via SSH.

If you just finished updating your Diretta Target, click [here](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target) to jump to the point-to-point network configuration steps for the Target.

---
> #### **A Note on Network Configuration: Why Not a Simple Bridge?**
>
> Users familiar with AudioLinux may wonder why this guide uses specific scripts to configure a routed point-to-point link with NAT instead of using the simpler network bridge option available in the `menu` system. This is a deliberate architectural choice made to achieve the highest possible level of network isolation.
>
> * A **network bridge** would place the Diretta Target directly on your main LAN, exposing it to all unrelated network broadcast and multicast traffic.
> * Our **routed setup** creates a completely separate, firewalled subnet. The Diretta Host protects the Target from all non-essential network chatter, ensuring the Target's processor only handles the audio stream. This minimizes system activity and potential electrical noise, which is the ultimate goal of this purist architecture.
>
> While a bridge is functionally simpler to set up, the routed method provides a theoretically superior foundation for audio performance by maximizing isolation.
---

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
    ```bash
    # Remove the old generic network file to prevent conflicts.
    sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
    ```

    Add an /etc/hosts entry for the Diretta Target:
    ```bash
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
    # Ensure nft is installed
    sudo pacman -S --noconfirm --needed nftables

    # Install firewall and NAT rules
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Flush all old rules from memory
    flush ruleset

    # Create a table named 'ip' (IPv4) called 'my_table'
    table ip my_table {

        # === Rule 2: Port Forwarding (DNAT) ===
        # This chain hooks into the 'prerouting' path for NAT
        chain prerouting {
            type nat hook prerouting priority -100;

            # Forward Host port 5101 to Target port 172.20.0.2:5001
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === Rule 3: Allow Forwarded Traffic (FILTER) ===
        # This chain hooks into the 'forward' path for packet filtering
        chain forward {
            type filter hook forward priority 0;

            # By default, drop all forwarded traffic
            policy drop;

            # Allow connections that are already established or related
            ct state established,related accept

            # Allow NEW traffic matching your port forward rule
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Allow all other NEW traffic from the Target subnet
            ip saddr 172.20.0.0/24 accept
        }

        # === Rule 1: Internet Access (MASQUERADE) ===
        # This chain hooks into the 'postrouting' path for NAT
        chain postrouting {
            type nat hook postrouting priority 100;

            # NAT (Masquerade) traffic from your subnet going
            # out any interface starting with 'enp' or 'wlp'
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # Stop and disable old iptables service if present (2>/dev/null suppresses errors if not present)
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Enable and apply rules via nft
    sudo systemctl enable --now nftables.service
    ```

4.  **Configure the Plugable USB to Ethernet Adapter**

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
    sudo sync && sudo poweroff
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
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Add an /etc/hosts entry for the Diretta Host. **Note:** Even if you selected a different network name for your Diretta Host, it's best for the Diretta Target to know your Host as `diretta-host`.
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
    sudo sync && sudo poweroff
    ```
2.  Disconnect both devices from your main LAN switch/router.
3.  Connect the **onboard Ethernet port** of the Diretta Host directly to the **onboard Ethernet port** of the Diretta Target using a single Ethernet cable.
4.  Plug the **USB-to-Ethernet adapter** into one of the blue USB 3.0 ports on the Diretta Host computer
5.  Connect the **USB-to-Ethernet adapter** on the Diretta Host to your main LAN switch/router.
6.  Power on both devices.

Upon booting, they will automatically use the new network configurations. **Note:** the IP address of your Diretta Host will likely have changed because it is now connected to your home network via the USB-to-Ethernet adapter. You'll have to return to your router's web UI or the Fing app to find the new address, which should be stable at this point.

```bash
cmd=$(cat <<'EOT'
read -rp "Enter the final address of your Diretta Host and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

You should now be able to ping the Target from the Host:
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

Also, you should be able to login to the Target from the Host:
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

From the target, let's try ping a host on the Internet to verify that the connection is working:
```bash
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
cmd=$(cat <<'EOT'
clear
# --- Interactive SSH Alias Setup Script ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Ensure the .ssh directory and config file exist with correct permissions ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Define the recommended global settings block ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Recommended Global SSH Settings ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Prepend global settings if they don't exist ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Adding recommended global SSH settings..."
  # Use a temporary file to prepend the settings
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ Recommended global SSH settings already exist. No changes made."
fi

# --- Add Diretta-specific host configurations ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ SSH configuration for 'diretta-host' already exists. No changes made."
else
  read -rp "Enter the LAN IP address of your Diretta Host and press [Enter]: " Diretta_Host_IP

  # Append the new configuration using a heredoc for clarity
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Diretta Configuration (added by script) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ SSH configuration for 'diretta-host' and 'diretta-target' has been added."
fi

# --- Clean up StrictHostKeyChecking from older versions of this guide ---
# This is no longer needed with the recommended SSH key setup
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Remove empty lines that might be left over
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Your ~/.ssh/config file now contains: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
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
**Note:** You are prompted once for the diretta-host (the jump box) and a second time for the diretta-target itself. The next section will replace this with seamless key-based authentication.

**Note:** You can use `ssh host` and `ssh target` for short.

#### 6.2. Recommended: Secure Authentication with SSH Keys

While you can use passwords, the most secure and convenient method is public key authentication. Our SSH configuration automates most of the process. After a one-time setup, you will be able to log in to both the Host and Target securely without typing a password.

**On your local computer:**

1.  **Create an SSH Key (if you don't already have one):**
    It's best practice to use a modern algorithm like `ed25519`. When prompted, enter a strong, memorable **passphrase**. This is not your login password; it's a password that protects your private key file itself.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Copy Your Public Key to the Devices:**
    These commands securely grant your key access to each device. The first command will prompt for the Diretta Host's password. Because that makes the connection to the Host passwordless, the second command will only prompt for the Diretta Target's password.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Log In Securely:**
    You can now SSH to your devices. The first time you connect to each one, you will be prompted for the **passphrase** you created in Step 1.

    ```bash
    ssh diretta-host
    ```

      * **On Linux:** Thanks to the `AddKeysToAgent yes` setting, your key will be added to the SSH agent for your current terminal session. You won't be prompted for the passphrase again until you reboot or start a new login session.

-----

### (Optional) For an Improved Linux Experience

If you are a Linux user and want your SSH key passphrase to persist across reboots (similar to the macOS experience), installing `keychain` is highly recommended.

  * **Install keychain (Ubuntu/Debian):**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Configure your shell:** Add the following line to your `~/.bashrc` (or `~/.zshrc`, `~/.profile`, etc.) to start `keychain` when you open a terminal. It will prompt for your passphrase only once, the first time you open a terminal after a reboot.

    ```bash
    eval `keychain --eval --quiet id_ed25519`
    ```

  * Reload your shell by opening a new terminal or running `source ~/.bashrc`.

You can now SSH to both devices (`ssh diretta-host`, `ssh diretta-target`) without being prompted for a password, securely authenticated by your SSH key.

---

### 7. Common System Optimizations

Please perform these steps on _both_ the Diretta Host and Target computers. If you do a `menu` update later, you will have to rerun the `sudoers` fix.

#### 7.1. Fix Systemd "Degraded" State

On a fresh AudioLinux installation, the system status is often reported as `degraded`. This is typically caused by a harmless inconsistency between the system's group files (`/etc/group` and `/etc/gshadow`). The following command safely synchronizes these files, which resolves the failed `shadow.service` and ensures a clean system state.

```bash
sudo grpconv
```

#### 7.2. Correct `sudoers` Rule Precedence

A default rule in the main `/etc/sudoers` file can sometimes override more specific rules needed for the web UI and other features. This can cause commands that should be passwordless to incorrectly ask for a password.

The following script safely corrects the order of rules in the `/etc/sudoers` file to ensure that specific exceptions are processed correctly. The script will only make changes if it detects the incorrect order.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Use a Perl filter to create a corrected version of the sudoers file.
# This script is idempotent and will not change a file that is already correct.
sudo cat "$SUDOERS_FILE" | perl -e '
while (<>) {
  if (m{/etc/sudoers.d} and not $found_audiolinux_all) {
    pop @lines if $#lines > -1 and $lines[$#lines] =~ /^$/;
    push @drop_in, $_;
  } else {
    push @lines, $_;
  }
  if (/^audiolinux ALL=\(ALL\) ALL$/) {
    $found_audiolinux_all++;
    push @lines, ("\n", @drop_in) if @drop_in;
  }
}
print @lines;
' > "$TEMP_SUDOERS"

# Validate the new file with visudo before installing
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Sudoers file passed validation. Installing corrected version..."
    # Use install to set correct ownership/permissions and replace the original
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "ERROR: The modified sudoers file failed validation. No changes were made." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Optimize Boot Time
To prevent a long boot delay while the system waits for a network connection, we will disable the "wait-online" service.
```bash
# Disable the network wait service to prevent long boot delays
sudo systemctl disable systemd-networkd-wait-online.service

# Create an override to make the MOTD script wait for a default route
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Create the Repair Script
The default behavior for Arch Linux is to leave the /boot filesystem in an unclean state if the computer is not shutdown cleanly. This is usually safe, but I've found that it can create a race condition when bringing up our private network. That, and users are likely to unplug these devices without shutting them down first. To protect against these issues, we'll add a workaround script that keeps the /boot filesystem (which is only changed during software updates) clean.

This script is safe to run both automatically at boot and manually on a live system.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Create the `systemd` Service File and enable the service
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
sudo systemctl --now enable boot-repair.service
sleep 5
journalctl -b -u boot-repair.service
```

#### 7.6. Minimize Disk I/O
Change `#Storage=auto` to `Storage=volatile` in `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Diretta Software Installation & Configuration

#### 8.1. On the Diretta Target

1.  Connect your USB DAC to one of the black USB 2.0 ports on the **Diretta Target** and ensure the DAC is powered on.
2.  SSH to the Target: `ssh diretta-target`.
3.  Configure Compatible Compiler Toolchain
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    source /etc/profile.d/llvm_diretta.sh
    ```
4.  Run `menu`.
5.  Select **AUDIO extra menu**.
6.  Select **DIRETTA target installation**. You will see the following menu:
    ```text
    What do you want to do?

    0) Install previous stable version
    1) Install/update last version
    2) Enable/Disable Diretta Target
    3) Configure Audio card
    4) Edit configuration
    5) Copy and edit new default configuration
    6) License
    7) Diretta Target log
    8) Exit

    ?
    ```
7.  You should perform these actions in sequence:
    * Choose **1) Install/update** to install the software.
    * Choose **2) Enable/Disable Diretta Target** and enable it.
    * Choose **3) Configure Audio card**. The system will list your available audio devices. Enter the card number corresponding to your USB DAC.
        ```text
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * Choose **4) Edit configuration**. Set `AlsaLatency=20` for a Raspberry Pi 5 Target or `AlsaLatency=40` for RPi4.
    * Choose **6) License**. The system will play hi-res (greater than 44.1 kHz PCM audio) for 6 minutes in trial mode. Follow the on-screen link and instructions to purchase and apply your full license for hi-res support. This requires the internet access we configured in step 5.
    * Choose **8) Exit**. Follow prompts to get back to the terminal

#### 8.2. On the Diretta Host

1.  SSH to the Host: `ssh diretta-host`.

2.  Configure Compatible Compiler Toolchain
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    source /etc/profile.d/llvm_diretta.sh
    ```

3.  Select **AUDIO extra menu**.

4.  Select **DIRETTA host installation/configuration**. You will see the following menu:
    ```text
    What do you want to do?

    0) Install previous stable version
    1) Install/update last version
    2) Enable/Disable Diretta daemon
    3) Set Ethernet interface
    4) Edit configuration
    5) Copy and edit new default configuration
    6) Diretta log
    7) Exit

    ?
    ```

5.  You should perform these actions in sequence:
    * Choose **1) Install/update** to install the software. *(Note: you may see `error: package 'lld' was not found. Don't worry, that will be corrected automatically by the installation)*
    * Choose **2) Enable/Disable Diretta daemon** and enable it.
    * Choose **3) Set Ethernet interface**. It is critical to select `end0`, the interface for the point-to-point link.
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enp1s0u1u2
        Please type the name of your preferred interface:
        end0
        ```
    * Choose **4) Edit configuration** only if you need to make advanced changes. The previous steps should be sufficient; however, here are some tuned settings you may wish to try:
        ```text
        TargetProfileLimitTime=0
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * If you just want to install the tuned parameters above, you can use this command block:
        ```bash
        cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
        [global]
        Interface=end0
        TargetProfileLimitTime=0
        ThredMode=1
        InfoCycle=100000
        FlexCycle=disable
        CycleTime=800
        CycleMinTime=
        Debug=stdout
        periodMax=32
        periodMin=16
        periodSizeMax=38400
        periodSizeMin=2048
        syncBufferCount=8
        alsaUnderrun=enable
        unInitMemDet=disable
        CpuSend=
        CpuOther=
        LatencyBuffer=0
        EOT
        ```
    * Choose **7) Exit**. Follow prompts to get back to the terminal

6.  Create an override to make the Diretta service auto-restart on failure
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Final Steps & Roon Integration

1.  Run `menu` if you exited back to the terminal after the previous step, otherwise go to the **Main menu**.

2.  **Install Roon Bridge (on Host):** If you use Roon, perform the following steps on the **Diretta Host**:
    * Run `menu`.
    * Select **INSTALL/UPDATE menu**.
    * Select **INSTALL/UPDATE Roonbridge**.
    * The installation will proceed. The installation may take a minute or two.


3.  **Enable Roon Bridge (on the Host):**
    * Select **Audio menu** from the Main menu
    * Select **SHOW audio service**
    * If you don't see **roonbridge** under enabled services, select **ROONBRIDGE enable/disable**

4.  **Reboot Both Devices:** For a clean start, reboot both the Target and Host, in that order:
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Configure Roon:**
    * Open Roon on your control device.
    * Go to `Settings` -> `Audio`.
    * Under the "Diretta" section, you should see your device. The name will be based on your DAC.
    * Click `Enable`, give it a name, and you are ready to play music!

Your dedicated Diretta link is now fully configured for pristine, isolated audio playback.
**Note:** The "Limited" zone for Diretta Target testing will disappear from Roon after six minutes of hi-res music playback. This is normal. At that point, you'll need to purchase a license for the Diretta Target. Cost is currently €100 and it can take up to 48 hours for activation to complete. You will receive two emails from the Diretta team. The first is your receipt; the second, your activation notification. Once you receive the activation email, restart your Target computer to pick up the activation.

> ---
> ### ✅ Checkpoint: Verify Your Core System
>
> Your core Diretta and Roon system should now be fully functional. To verify all services and connections, please proceed to [**Appendix 5**](#14-appendix-5-system-health-checks) and run the universal **System Health Check** command on both the Host and the Target.
>
> ---

---

## 10. Appendix 1: Optional Argon ONE Fan Control
If you decided to use an Argon ONE case for your Raspberry Pi, the default installer script assumes you're running a Debian O/S. However Audiolinux is based on Arch Linux, so you'll have to follow these steps instead.

If you are using Argon ONE cases for both Diretta Host and Target, you'll need to perform these steps on both computers.

### Step 1: Skip the `argon1.sh` script in the manual
The manual says to download the argon1.sh script from download.argon40.com and pipe it to `bash`. This won't work on Audiolinux since the script assumes a Debian-based O/S, so skip this step and follow the steps below instead.

### Step 2: Configure your system:
These commands will enable the I2C interface and add the specific `dtoverlay`
for the Argon ONE case. The script first attempts to uncomment the `i2c_arm`
parameter if it's commented out and then adds the `argonone` overlay if it's
missing, preventing errors and duplicate entries.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- Enable I2C by uncommenting the line if it exists ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Step 3: Configure `udev` permissions
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Step 4: Install the Argon One Package
```bash
yay -S argonone-c-git
```

### Step 5: Switch Argon ONE case from hardware to software control
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# Create systemd overrides to switch the case to software mode on boot
sudo mkdir -pv /etc/systemd/system/argononed.service.d
cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/software-mode.conf
[Service]
ExecStartPre=/bin/sh -c "while [ ! -e /dev/i2c-1 ]; do sleep 0.1; done && /usr/bin/i2cset -y 1 0x1a 0"
EOT

cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/override.conf
[Unit]
After=multi-user.target
EOT
```

### Step 6: Enable the Service
```bash
# Reload the systemd manager to read the new configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable argononed.service
```

### Step 7: Reboot
Finally, reboot your Raspberry Pi for all changes to take effect (Target first, then Host):
```bash
sudo sync && sudo reboot
```

Now, the fan will be controlled by the daemon, and the power button will have full functionality.

### Step 8: Verify the service
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Step 9: Review Fan Mode and Settings:
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
sleep 5
sudo argonone-cli --decode
```

Now, feel free to adjust the values as needed, following the steps above.

---

## 11. Appendix 2: Optional IR Remote Control

This guide provides instructions for installing and configuring an IR remote to control Roon. The setup is divided into two parts.

  * **Part 1** covers the hardware-specific setup. You will choose **one** of the two appendices depending on whether you are using the Flirc USB receiver or the Argon One case's built-in receiver.
  * **Part 2** covers the software setup for the `roon-ir-remote` control script, which is identical for both hardware options.

**Note:** You will _only_ perform these steps on the Diretta Host. The Target should not be used for relaying IR remote control commands to Roon Server.

---

### **Part 1: IR Receiver Hardware Setup**

*Follow the appendix for the hardware you are using.*

#### **Option 1: Flirc USB IR Receiver Setup**

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

3.  Skip to [Part 2: Control Script Software Setup](#part-2-control-script-software-setup)

---

#### **Option 2: Argon One IR Remote Setup**

1.  **Enable the IR Receiver Hardware:**
    You must enable the hardware overlay for the Argon One case's IR receiver.

      * This command will safely add the required hardware overlay to your `/boot/config.txt` file, first checking to ensure it isn't added more than once.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # Add IR remote overlay if it's not already there
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Enabling Argon One IR Receiver..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Argon One IR Receiver already enabled."
        fi
        ```
      * A reboot is required for the hardware change to take effect.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **Install IR Tools and Enable Protocols:**
    Install `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Capture Button Scancodes:**
     Enable all kernel protocols so it can decode signals from your remote.Run the test tool to see the unique scancode for each remote button.
    ```bash
    sudo ir-keytable -p all
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

### **Part 2: Control Script Software Setup**

*After setting up your hardware in Part 1, follow these steps to install and configure the Python control script.*

### **Step 1: Add `audiolinux` to the `input` group**
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

---

### **Step 2: Install Python via `pyenv`**

Install `pyenv` and the latest stable version of Python.

```bash
# Install build dependencies
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Install pyenv only if it's not already installed
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Installing pyenv ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- pyenv is already installed. Skipping installation. ---"
fi

# Configure shell for pyenv
if grep -q 'pyenv init' ~/.bashrc; then
  :
else
  cat <<'EOT'>> ~/.bashrc

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"
EOT
fi

# Source the file to make pyenv available in the current shell
. ~/.bashrc

# Install and set the latest Python version only if it's not already installed
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
  echo "--- Installing Python ${PYVER}. This will take several minutes... ---"
  pyenv install $PYVER
else
  echo "--- Python ${PYVER} is already installed. Skipping installation. ---"
fi

# Set the global Python version
pyenv global $PYVER
```

**Note:** It's normal for the `Installing Python-3.14.0...` part to take ~10 minutes as it compiles Python from source. Don't give up! Feel free to relax to some beautiful music using your new Diretta zone in Roon while you wait. It should be available while Python is installing on the Host.

---

### **Step 3: Download `roon-ir-remote` Software Repo**

Clone the script repository and fetch a patch to correctly handle keycodes by name instead of by number.

```bash
cd
# Clone the repo if it doesn't exist, otherwise update it
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Step 4: Create the Roon Environment Config File**

Configure the script with your Roon details. **Note:** The `event_mapping` codes must match the key names you defined in your hardware setup (`KEY_ENTER`, `KEY_VOLUMEUP`, etc.).

```bash
bash <<'EOF'
# --- Start of Script ---

# Get Roon Zone and store it in a variable
echo "Enter the name of your Roon zone."
echo "IMPORTANT: This must match the zone name in the Roon app exactly (case-sensitive)."
# This line is the fix: < /dev/tty tells read to use the terminal
read -rp "Enter your Roon Zone name: " MY_ROON_ZONE < /dev/tty

# Ensure the target directory exists
mkdir -p roon-ir-remote

# Create the configuration file using a Here Document
# The variable will now be correctly substituted
cat <<EOD > roon-ir-remote/app_info.json
{
  "roon": {
    "app_info": {
      "extension_id": "com.smangels.roon-ir-remote",
      "display_name": "Roon IR Remote",
      "display_version": "1.1.0",
      "publisher": "dsnyder",
      "email": "dsnyder0cnn@gmail.com",
      "website": "https://github.com/dsnyder0pc/roon-ir-remote"
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
EOD

echo ""
echo "✅ Configuration file 'roon-ir-remote/app_info.json' created successfully."

# --- End of Script ---
EOF
```

---

### **Step 5: Prepare and Test `roon-ir-remote`**

Install the script's dependencies into a virtual environment and run it for the first time.

```bash
cd ~/roon-ir-remote
# Create the virtual environment only if it doesn't already exist
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Creating 'roon-ir-remote' virtual environment ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- 'roon-ir-remote' virtual environment already exists ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

The first time you run the script, you must **authorize the extension in Roon** by going to `Settings` -> `Extensions`.

With music playing in your new Diretta Roon zone, point your IR remote control directly at the Diretta Host computer and press the Play/Pause button (may be the center button in the 5-way controller). Also try Next and Previous. If these are not working, check your terminal window for any error messages.  Once you are finished testing, type `CTRL-C` to exit.

---

### **Step 6: Create a `systemd` Service**

Create a service to run the script automatically in the background.

```bash
cat <<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
After=network-online.target
Wants=network-online.target

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

### **Step 7: Watch the logs for a bit:**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Type `CTRL-C` once you're satisfied that things are working as expected.

---

### **Step 8: Install `set-roon-zone` script**
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

**Note: A Better Way to Set the Zone**
While this script works perfectly, the recommended method for changing the Roon Zone is to use the AnCaolas Link System Control web application, detailed in [Appendix 4](#13-appendix-4-optional-system-control-web-ui). The web UI provides a dedicated page for viewing and editing the zone name from your phone or browser.

### **Step 9: Profit! 📈**

> ---
> ### ✅ Checkpoint: Verify Your IR Remote Setup
>
> Your IR Remote hardware and software should now be configured. To verify the setup, proceed to [**Appendix 5**](#14-appendix-5-system-health-checks) and run the universal **System Health Check** command on the Diretta Host.
>
> ---

Your IR remote should now control Roon. Enjoy!

---

## 12. Appendix 3: Optional Purist Mode
There is minimal network and background activity on the Diretta Target computer that is not related to music playback using the Diretta protocol. However, some users prefer to take extra steps to reduce the possibility of such activity. We are already on the extreme edge of audio performance, so why not?

---
> CRITICAL WARNING: For the Diretta Target ONLY
>
> The `purist-mode` script and all instructions in this appendix are designed exclusively for the Diretta Target.
>
> Do NOT install or run this script on the Diretta Host. Doing so will drop the Host's connection to your main network, making it unreachable and unable to communicate with your Roon Core or streaming services. This would render the entire system inoperable until you can gain console access (with a physical keyboard and monitor) to revert the changes.
---

### Step 1: Install the `purist-mode` script **(only on the Diretta Target computer)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Script for showing Purist Mode status on login
cat <<'EOT' | sudo tee /etc/profile.d/purist-status.sh
#!/bin/sh
BACKUP_FILE="/etc/nsswitch.conf.purist-bak"

if [ -f "$BACKUP_FILE" ]; then
    echo -e '\n\e[1;32m✅ Purist Mode is ACTIVE.\e[0m System optimized for the highest sound quality.'
else
    echo -e '\n\e[1;33m⚠️ CAUTION: Purist Mode is DISABLED.\e[0m Background activity may impact sound quality.'
fi
EOT
```

To run it, simply login to the Diretta Target and type `purist-mode`:
```bash
purist-mode
```

For example:
```text
[audiolinux@diretta-target ~]$ purist-mode
This script requires sudo privileges. You may be prompted for a password.
🚀 Activating Purist Mode...
  -> Stopping time synchronization service (chronyd)...
  -> Disabling DNS lookups...
  -> Dropping default gateway...

✅ Purist Mode is ACTIVE.
```

Listen for a while to see if you prefer the sound (or peace of mind).

---

### Step 2: Enable Purist Mode by Default

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

---

### Step 3: Install a wrapper around the `menu` command
Many functions in the AudioLinux require Internet access. To keep things working as expected, add a wrapper around the `menu` command that disables Purist mode while you are using the menu, enabling it again when you exit to the terminal.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Add a wrapper around the menu command"
  cat <<'EOT' | tee -a ~/.bashrc

# Custom wrapper for the AudioLinux menu to manage Purist Mode
menu_wrapper() {
  local was_active=false
  # Check the initial state of Purist Mode by looking for the backup file.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # If Purist Mode was active, temporarily revert it for the menu.
  if [ "$was_active" = true ]; then
    echo "Checking credentials to manage Purist Mode..."
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

### Understanding the Purist Mode States

The Purist Mode system is designed to be flexible, allowing you to control it manually or have it activate automatically after the system boots. It operates in two primary states:

  * **Disabled (Standard Mode):**
    This is the normal, fully functional state of the Diretta Target. The network gateway is active, all services (`chronyd`, `argononed`) are running, and the device operates without restrictions.

  * **Active (Purist Mode):**
    This is the optimized state for critical listening. The network gateway is dropped to prevent internet traffic, and non-essential background services (including the Argon ONE fan) are stopped to minimize all potential system interference.

These states are managed in two ways: **automatically** on boot and **manually** via the command line.

#### Automatic Control (On Boot)

The boot-up process is designed to be safe and predictable, with an optional automated switch to Purist Mode.

1.  **Mandatory Revert on Boot:** Regardless of the state it was in when shut down, the Diretta Target **always** boots into **Standard Mode** first. This is a critical feature that ensures essential services like network time synchronization can run correctly.

2.  **Optional Auto-Activation:** If you have enabled the automatic feature, the system will wait 60 seconds after booting and then automatically switch to **Purist Mode**. This provides a "set it and forget it" experience for users who always prefer listening in the optimized state.

#### Manual Control (Interactive Use)

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

## 13. Appendix 4: Optional System Control Web UI

This appendix provides instructions for installing a simple web-based application on the Diretta Host. This application provides an easy-to-use interface, accessible from a phone or tablet, to manage key features of your Diretta system, including Purist Mode on the Target and Roon IR Remote integration settings on the Host.

> **CRITICAL WARNING: Perform these steps carefully.**
> This setup involves creating a new user and modifying security settings. Follow the instructions precisely to ensure the system remains secure and functional.

The setup is divided into two parts: first, we configure the **Diretta Target** to securely accept commands, and second, we install the web application on the **Diretta Host**. However, pay attention because we swap between hosts frequently.

---

### **Part 1: Diretta Target Configuration**

On the **Diretta Target**, we will create a new user with very limited permissions. This user will only be allowed to run the specific commands needed to manage Purist Mode.

1.  **SSH to the Diretta Target:**
    ```bash
    ssh diretta-target
    ```

2.  **Create a New User for the App:**
    This command creates a new user named `purist-app` and its home directory. A valid shell is required for non-interactive SSH commands to function.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Create Secure Command Scripts:**
    We will create four small, dedicated scripts that are the *only* actions the web app is allowed to perform. This is a critical security step.
    ```bash
    # Script to get the current status, including license state
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    LICENSE_LIMITED="false"

    # Check for Purist Mode
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      IS_ACTIVE="true"
    fi

    # Check if auto-start is enabled
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      IS_AUTO_ENABLED="true"
    fi

    # Check for the presence of the Diretta License Key File
    if ! ls /opt/diretta-alsa-target/ | grep -qv '^diretta'; then
      LICENSE_LIMITED="true"
    fi

    # Output all status flags as a single JSON object
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
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

    # Create the script to restart the Diretta service
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Restarts the Diretta ALSA Target service.
    # This script is intended to be called via sudo by the purist-app user.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Create the script to fetch the Diretta License URL
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # This script's only job is to read the cache file created at boot.
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # If the cache exists and has content, display it.
        cat "$CACHE_FILE"
    else
        # If not, print a helpful error to stderr and exit.
        echo "Error: License cache not found or is empty." >&2
        exit 1
    fi
    EOT

    # Make the new scripts executable
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Grant Sudo Permissions:**
    This step allows the `purist-app` user to run our four new scripts with root privileges and without needing an interactive terminal.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # Tell sudo not to require a TTY for the purist-app user
    Defaults:purist-app !requiretty

    # Allow the purist-app user to run the specific control scripts without a password
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
    EOT
    ```

5.  **Populate the Diretta License Cache File at Boot Time**
    Fetching the Diretta License URL requires an Internet connection. If we have Purist Mode enabled by default, the Target will never be able to fetch the URL. However, at boot time, we have Purist Mode disabled for 60 seconds in order to set the clock and check for a Diretta License activation. We can use that time window to fetch the URL also.
    ```bash
    # Download the script, set correct permissions, and place it in the system path
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Create the Systemd Drop-in File
    sudo mkdir -p /etc/systemd/system/purist-mode-revert-on-boot.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-revert-on-boot.service.d/create-cache.conf
    [Service]
    ExecStartPost=/usr/local/bin/create-diretta-cache.sh
    EOT

    # Go ahead and run the script manually once
    sudo /usr/local/bin/create-diretta-cache.sh
    ```

---

### **Part 2: Diretta Host Configuration**

Now, on the **Diretta Host**, we will perform all the steps to install and configure the web application. You should be logged in as the `audiolinux` user for this entire section.

1.  **SSH to the Diretta Host:**
    ```bash
    ssh diretta-host
    ```

2.  **Generate a Dedicated SSH Key:**
    This creates a new SSH key pair specifically for the web app. It will have no passphrase.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Copy the Key to the Target:**
    This step will securely copy the public key to the Target.
    ```bash
    echo "--- Authorizing the new SSH key on the Diretta Target ---"

    # Step A: Copy the public key to the Target's home directory
    echo "--> Copying public key to the Target..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Authorize the Key on the Target:**
    ```bash
    ssh diretta-target

    ```

    Once you are logged in to the Target, run this script to set up the key for the 'purist-app' user
    ```bash
    echo "--> Running setup script on the Target..."
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

    echo "✅ SSH key has been successfully authorized on the Target."
    ```

5.  **Manually Test the Remote Commands (Recommended):**
    Before starting the web app, test each of the remote commands from the **Diretta Host's** terminal to confirm the backend is working.
    ```bash
    # Test the Status Command (should return a JSON string)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Test Toggling Purist Mode (run this twice to turn it on, then off)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-toggle-mode'

    # Test Toggling Auto-Start on Boot (run this twice to enable, then disable)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-toggle-auto'

    # Test Fetching the Diretta Target License URL
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'

    # Test Restarting the Diretta Target Service
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-restart-target'
    ```

6.  **Install Python via pyenv** on the **Diretta Host** (feel free to skip this step if you did this already to get the IR Remote working)
    Install `pyenv` and the latest stable version of Python.
    ```bash
    # Install build dependencies
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # Install pyenv only if it's not already installed
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- Installing pyenv ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- pyenv is already installed. Skipping installation. ---"
    fi

    # Configure shell for pyenv
    if grep -q 'pyenv init' ~/.bashrc; then
      :
    else
      cat <<'EOT'>> ~/.bashrc

    export PYENV_ROOT="$HOME/.pyenv"
    [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init - bash)"
    eval "$(pyenv virtualenv-init -)"
    EOT
    fi

    # Source the file to make pyenv available in the current shell
    . ~/.bashrc

    # Install and set the latest Python version only if it's not already installed
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      echo "--- Installing Python ${PYVER}. This will take several minutes... ---"
      pyenv install $PYVER
    else
      echo "--- Python ${PYVER} is already installed. Skipping installation. ---"
    fi

    # Set the global Python version
    pyenv global $PYVER
    ```

    **Note:** It's normal for the `Installing Python-3.14.0...` part to take ~10 minutes as it compiles Python from source. Don't give up! Feel free to relax to some beautiful music using your new Diretta zone in Roon while you wait. It should be available while Python is installing on the Host.

7.  **Install Avahi and Python Dependencies on the Diretta Host:**

    **Note:** OPTIONAL - If you have more than one Diretta Host on your network, please make sure that they have unique names. You can use a command like the following to rename this one before proceeding:

    ```bash
    # Optionally rename the Diretta Host if this is your second build on the same network
    sudo hostnamectl set-hostname diretta-host2
    ```

    This step runs on the **Diretta Host**. It installs the Avahi daemon and uses a `requirements.txt` file to install Flask into a dedicated virtual environment.
    ```bash
    # Install Avahi for .local name resolution
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Dynamically find the USB Ethernet interface name (e.g., enp1s0u1u2)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/enp/{print $2}')

    # Create a configuration override for Avahi to isolate it to the USB interface
    echo "--- Configuring Avahi to use interface: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Enable and start the Avahi daemon
    sudo systemctl enable --now avahi-daemon.service

    # Create the application directory and the requirements file
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Create a virtual environment and install dependencies
    echo "--- Setting up Python environment for the Web UI ---"
    # Create the virtual environment only if it doesn't already exist
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- Creating 'purist-webui' virtual environment ---"
      pyenv virtualenv purist-webui
    else
      echo "--- 'purist-webui' virtual environment already exists ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Install the Flask App:**
    Download the Python script directly from GitHub into the application directory on the **Diretta Host**.
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **Grant Port-Binding Capability**
    We need to give the Python exutable permission to bind to port 80 on the Diretta Host for our web app to start.
    ```bash
    # Install the package that provides the 'setcap' command
    sudo pacman -S --noconfirm --needed libcap

    # Find the real path to the Python executable, resolving all symbolic links
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Grant the port-binding capability directly to the final Python executable
    echo "Applying capability to the real file: ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Grant Sudo Permissions on the Host:**
    This step is critical for allowing the web application to restart the necessary Roon-related services without a password.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # Allow the webui (running as audiolinux) to restart required services
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Test the Flask App Interactively:**
    Now, run the app from the command line on the **Diretta Host** to ensure it starts correctly.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    You should see output indicating the Flask server has started on port **8080**. From another device, access [http://diretta-host.local:8080](http://diretta-host.local:8080). If it works, return to the SSH terminal and press `Ctrl+C` to stop the server.

12. **Create the `systemd` Service:**
    This service will run the web app automatically the **Diretta Host**, using the correct Python executable from our `pyenv` virtual environment.
    ```bash
    cat <<EOT | sudo tee /etc/systemd/system/purist-webui.service
    [Unit]
    Description=Purist Mode Web UI
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    User=${LOGNAME}
    Group=${LOGNAME}
    WorkingDirectory=/home/${LOGNAME}/purist-mode-webui
    ExecStart=/home/${LOGNAME}/.pyenv/versions/purist-webui/bin/python app.py
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    EOT
    ```

13. **Enable and Start the Web App:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now purist-webui.service
    ```

14. **Watch the logs for a bit:**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Test the web UI with the final URL:**
    Open a browser to [http://diretta-host.local](http://diretta-host.local) and watch the logs for any errors.

Type `CTRL-C` once you're satisfied that things are working as expected.

---

### **Access the Web UI**

You're all set! Open a web browser on your phone, tablet, or computer connected to the same network as the Diretta Host. Navigate to the main landing page:

[http://diretta-host.local](http://diretta-host.local)

---
> **A Note on Browser Security Warnings**
> When you first visit http://diretta-host.local, your browser will likely display a security warning stating that the connection is not secure. This is expected and safe to bypass. The warning appears because the connection uses standard `HTTP` instead of encrypted `HTTPS`, an intentional choice to minimize processing overhead on the audio device. Because the app runs only on your private home network and handles no sensitive data, you can confidently click "Continue to site."
---

From the landing page, a navigation bar at the top will guide you to the different control panels:

* **Home:** The main landing page with links to the different applications.

* **Purist Mode App:** This page contains the controls for toggling Purist Mode and its auto-start behavior on the Diretta Target. It automatically refreshes every 30 seconds to show the current status. It also contains the "Restart Services" button for use after a Diretta license activation.

* **IR Remote App:** If you have completed the IR remote setup (Appendix 2), this link will appear. This page provides a simple form to view and update the Roon Zone name your remote will control. This page does not auto-refresh, so you can take as long as you need to make your edits.

> ---
> ### ✅ Checkpoint: Verify Your Web UI Setup
>
> The Purist Mode Web UI should now be operational. To verify all components of this complex feature, proceed to [**Appendix 5**](#14-appendix-5-system-health-checks) and run the universal **System Health Check** command on both the Host and the Target.
>
> ---


## 14. Appendix 5: System Health Checks

After completing major sections of this guide, it's a good idea to run a quick quality assurance (QA) check to verify that everything is configured correctly.

We've created a smart script that automatically detects whether you are running it on the **Diretta Host** or the **Diretta Target** and performs the appropriate set of checks.

**How to Run the Check**

On either the Host or the Target, run the following single command. It will download and execute the QA script, providing a detailed report of your system's status.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Appendix 6: Advanced Realtime Performance Tuning

The following steps are optional but recommended for users seeking to extract the absolute maximum performance from their Diretta setup. The strategy, based on advice from AudioLinux author Piero, is to create the most stable and electrically quiet environment possible on both the Host and Target devices.

This is achieved by using **CPU isolation** to dedicate specific processor cores to audio tasks, shielding them from the operating system, and carefully tuning **realtime priorities** to ensure the audio data path is never interrupted.

> **Note:** This is an advanced tuning process. Please ensure your core Diretta system is fully functional by completing sections 1-9 of the main guide before proceeding. Proper cooling for both Raspberry Pi devices is essential.

---

### **Part 1: Optimizing the Diretta Target (RPi5)**

The goal for the Target is to make it a pure, low-latency audio endpoint. We will isolate the Diretta application on a single, dedicated CPU core and give it a high, but not excessive, realtime priority.

#### **Step 6.1: Isolate a CPU Core for the Audio Application**

This step dedicates one CPU core exclusively to the Diretta Target application.

1.  SSH to the Diretta Target:
    ```bash
    ssh diretta-target
    ```
2.  Enter the AudioLinux menu system:
    ```bash
    menu
    ```
3.  Navigate to the **ISOLATED CPU CORES configuration** menu (under **SYSTEM menu**).

4.  Disable any previous settings as shown below:
    ```text
    Please chose your option:
    1) Configure and enable
    2) Disable
    3) Exit
    ?
    2

    ISOLATED CORES has been reset

    IRQ balancer was disabled
    It can be enabled in Expert menu

    PRESS RETURN TO EXIT
    ```

5.  Navigate back to the **ISOLATED CPU CORES configuration** menu (under **SYSTEM menu**). Follow the prompts exactly as shown below to isolate **cores 2 and 3** and assign the Diretta application to it.
    ```text
    Please chose your option:
    1) Configure and enable
    2) Disable
    3) Exit
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the application(s) that should be confined to group 1...:
    ?diretta_app_target

    Please type the Address (iSerial) number of your card(s)...:
    (Press ENTER if you don't want to assign IRQ to this group):
    ?end0
    ```
6.  After the process completes, press **ENTER** to exit back to the System menu. **Do not reboot yet.**

> **A Note on Automatic IRQ Affinity:** You may notice the script reports that it has also isolated the `end0` network IRQs to the same core. This is not a bug, but an intelligent optimization. The script automatically pins the network interrupts to the same core as the application using the network, creating the most efficient data path possible.

---

#### **Step 6.2: Set Realtime Priority**

Next, we will give the Diretta application a "not too high" priority, ensuring it runs smoothly without interfering with the more critical USB audio interrupts.

1.  Also under the **SYSTEM menu**, navigate to the **REALTIME PRIORITY configuration** menu.
2.  Select **Option 3) Configure IRQ priority**.
3.  Follow the prompts to make sure there's a default IRQ Priority
    ```text
    Do you want to set the IRQ priority for each device? (1/2)
    1 - IRQ priority (advanced)
    2 - IRQ priority (simple)
    3 - Exit
    ?2

    -> Your previous configuration has been saved to /etc/rtpriority/rtirqs.conf.bak
    Please type xhci (default) or snd for internal cards
    ?xhci

    The max. available realtime priority is 98
    Suggested values are 95 (extreme) or 90 (default)
    Please enter your value:
    ?90

    Do you want to set the IRQ priority for each device? (1/2)
    1 - IRQ priority (advanced)
    2 - IRQ priority (simple)
    3 - Exit
    ?3
    ```
4.  Select **Option 4) Configure APPLICATION priority**.
5.  Follow the prompts to set a **manual** priority of **70**.

    ```text
    ...
    Type Y if you want to edit it
    ?
    [PRESS ENTER]

    Here you will configure the max. priority given to audio applications...
    ?70

    Now you can configure your preferred method...
    ?manual
    ```
6.  After confirming the changes, select **5) Exit** and return to the command line.
7.  Reboot the Diretta Target for all changes to take effect.
    ```bash
    sudo sync && sudo reboot
    ```

---

### **Part 2: Optimizing the Diretta Host (RPi4)**

The goal for the Host is to give Roon Bridge and the Diretta service dedicated processing resources, but without using high realtime priorities. CPU isolation is a more powerful tool here, as it prevents the processes from being interrupted in the first place.

#### **Step 6.3: Isolate CPU Cores for Audio Applications**

This step dedicates two CPU cores to handle both Roon Bridge and the Diretta Host service.

1.  SSH to the Diretta Host:
    ```bash
    ssh diretta-host
    ```
2.  Enter the AudioLinux menu system:
    ```bash
    menu
    ```
3.  Navigate to the **ISOLATED CPU CORES configuration** menu (under **SYSTEM menu**).

4.  Disable any previous settings as shown below:
    ```text
    Please chose your option:
    1) Configure and enable
    2) Disable
    3) Exit
    ?
    2

    ISOLATED CORES has been reset

    IRQ balancer was disabled
    It can be enabled in Expert menu

    PRESS RETURN TO EXIT
    ```

5.  Navigate back to the **ISOLATED CPU CORES configuration** menu (under **SYSTEM menu**). Follow the prompts to isolate **cores 2 and 3** and assign the relevant applications.

    ```text
    Please chose your option:
    1) Configure and enable
    ...
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the application(s) that should be confined to group 1...:
    ?RoonBridge syncAlsa

    Please type the Address (iSerial) number of your card(s)...:
    (Press ENTER if you don't want to assign IRQ to this group):
    ?end0
    ```

6.  After the process completes, press **ENTER** to exit back to the System menu. **Do not reboot yet.**

---

#### **Step 6.4: Disable Application Realtime Priority**

With our audio applications running on dedicated cores, they no longer need to compete for CPU time. Forcing a high realtime priority is now unnecessary and can be counterproductive. We will disable the service entirely on the Host.

1.  Also under the **SYSTEM menu**, navigate to the **REALTIME PRIORITY configuration** menu.
2.  Select **Option 2) Enable/disable APPLICATION service (rtapp)**. This will immediately disable the service.
3.  Select **5) Exit** and return to the command line.
4.  Reboot the Diretta Host.
    ```bash
    sudo sync && sudo reboot
    ```

-----

#### **Step 6.5: Reduce Diretta `CycleTime`**

With the real-time kernel optimizations in place, the Diretta Host can now handle a more aggressive packet interval, which can lead to improved sound quality. This final step reduces the `CycleTime` parameter from 800 to 514 microseconds. This smaller timing gap between packets ensures that that all content up to DSD256 and DXD (32-bit, 352.8 kHz) will require only one packet per cycle.

1.  SSH to the **Diretta Host** if you are not still logged in.
2.  Run the following command to apply the optimized setting:
    ```bash
    cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
    [global]
    Interface=end0
    TargetProfileLimitTime=0
    ThredMode=1
    InfoCycle=100000
    FlexCycle=disable
    CycleTime=514
    CycleMinTime=
    Debug=stdout
    periodMax=32
    periodMin=16
    periodSizeMax=38400
    periodSizeMin=2048
    syncBufferCount=8
    alsaUnderrun=enable
    unInitMemDet=disable
    CpuSend=
    CpuOther=
    LatencyBuffer=0
    EOT
    ```
3.  Restart the Diretta service for the change to take effect:
    ```bash
    sudo systemctl restart diretta_alsa.service
    ```

-----

> ---
> ### ✅ Checkpoint: Verify Your Realtime Tuning
>
> Your advanced realtime tuning should now be complete. To verify all components of this new configuration, please return to [**Appendix 5**](#14-appendix-5-system-health-checks) and run the universal **System Health Check** command on both the Host and the Target.
>
> ---

## 16. Appendix 7: Optimize CPU with Event-Driven Hooks

This appendix provides an advanced optimization to further reduce system jitter and needless CPU activity.

The default AudioLinux configuration includes background "timers" (e.g., `isolated_app.timer`, `rtapp.timer`) that run tuning scripts once per minute. While effective, these timers cause periodic CPU spikes, which is contrary to our goal of a quiet, stable system.

This guide will replace that "periodic" behavior with an "event-driven" one. We will **disable the timers** and instead use `systemd` drop-in files to run these tuning scripts **only once** when the main audio services start. This "set it and forget it" approach eliminates the one-minute CPU spikes entirely.

-----

### **Part 1: Optimizing the Diretta Target**

On the Target, we will disable both `isolated_app.timer` and `rtapp.timer` and hook their scripts into the `diretta_alsa_target.service`.

1.  SSH to the Diretta Target:

    ```bash
    ssh diretta-target
    ```

2.  **Stop and Disable the Timers:**
    This command permanently stops the timers from running and removes their auto-start links.

    ```bash
    sudo systemctl stop isolated_app.timer rtapp.timer
    sudo systemctl disable isolated_app.timer rtapp.timer
    ```

3.  **Create the Systemd Drop-in Hook:**
    This command creates a new configuration file that instructs `systemd` to run the two scripts *after* the main `diretta_alsa_target.service` starts.

    ```bash
    # Create the directory
    sudo mkdir -p /etc/systemd/system/diretta_alsa_target.service.d/

    # Create the drop-in file
    sudo bash -c 'cat <<EOF > /etc/systemd/system/diretta_alsa_target.service.d/10-local-hooks.conf
    [Service]
    ExecStartPost=/opt/scripts/system/isolated_app.sh
    ExecStartPost=-/bin/bash /usr/bin/rtapp
    ExecReloadPost=/opt/scripts/system/isolated_app.sh
    ExecReloadPost=-/bin/bash /usr/bin/rtapp
    EOF'
    ```

    > **Note on the Hyphen (`-`):**
    > The prefix `-` before the `/bin/bash /usr/bin/rtapp` command is intentional. The `rtapp` script may fail to run in this context (exiting with a non-zero status). The hyphen tells `systemd` to "ignore failure" for this specific command, allowing the main `diretta_alsa_target.service` to continue running.

4.  **Reload Systemd and Restart the Service:**

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa_target.service
    ```

5.  **Verify the Changes:**

    ```bash
    systemctl status diretta_alsa_target.service
    ```

    In the output, you should see that the service is `Active: active (running)`. You should also see two `Process:` lines, one for `isolated_app.sh` (which should show `status=0/SUCCESS`) and one for `rtapp` (which will likely show `status=1/FAILURE`). This is the correct and expected outcome.

-----

### **Part 2: Optimizing the Diretta Host**

On the Host, we will disable the `isolated_app.timer` and hook its script into *both* the `roonbridge.service` and `diretta_alsa.service`. This ensures the optimizations are applied regardless of which service starts first.

1.  SSH to the Diretta Host:

    ```bash
    ssh diretta-host
    ```

2.  **Stop and Disable the Timer:**

    ```bash
    sudo systemctl stop isolated_app.timer
    sudo systemctl disable isolated_app.timer
    ```

3.  **Create the Systemd Drop-in Hooks:**
    We must create two separate drop-in files, one for each service.

    **For `roonbridge.service`:**

    ```bash
    # Create the directory
    sudo mkdir -p /etc/systemd/system/roonbridge.service.d/

    # Create the drop-in file
    sudo bash -c 'cat <<EOF > /etc/systemd/system/roonbridge.service.d/10-local-hooks.conf
    [Service]
    ExecStartPost=/opt/scripts/system/isolated_app.sh
    ExecReloadPost=/opt/scripts/system/isolated_app.sh
    EOF'
    ```

    **For `diretta_alsa.service`:**

    ```bash
    # Create the directory
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d/

    # Create the drop-in file
    sudo bash -c 'cat <<EOF > /etc/systemd/system/diretta_alsa.service.d/10-local-hooks.conf
    [Service]
    ExecStartPost=/opt/scripts/system/isolated_app.sh
    ExecReloadPost=/opt/scripts/system/isolated_app.sh
    EOF'
    ```

4.  **Reload Systemd and Restart the Services:**

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart roonbridge.service
    sudo systemctl restart diretta_alsa.service
    ```

5.  **Verify the Changes:**
    Check the status of both services.

    ```bash
    systemctl status roonbridge.service
    systemctl status diretta_alsa.service
    ```

    For both services, you should see `Active: active (running)` and a `Process:` line for `isolated_app.sh` showing `status=0/SUCCESS`.

>
>
> -----
>
> ### ✅ Checkpoint: Verify Your CPU Optimizations
>
> Your system is now optimized to run its tuning scripts only at boot, eliminating periodic CPU spikes. To verify this new configuration is working correctly with the rest of the system, please return to [**Appendix 5**](#14-appendix-5-system-health-checks) and run the universal **System Health Check** command on both the Host and the Target.
>
> -----

## 17. Appendix 8: Optional Purist 100Mbps Network Mode

**Objective:** Reduce electrical noise and improve OS scheduler precision by limiting the dedicated network link to 100 Mbps.

While counter-intuitive, reducing the link speed from 1 Gbps to 100 Mbps on the dedicated link (`end0`) can improve sound quality. The lower operating frequency of 100BASE-TX (31.25 MHz vs 62.5 MHz) generates less RFI, and benchmarks have shown this reduces "Core Jitter" on the Host CPU by ~14%.

**Note:** You may see "buffer low" warnings in the Target logs (`LatencyBuffer` dropping to 1). This is normal behavior due to the increased serialization latency of the slower link and does not cause audible dropouts.

### Step 1: Configure the Host

We will create a systemd service on the **Host** that forces it to advertise *only* 100 Mbps Full Duplex. The Target will automatically detect this and match it.

1.  **Create the restriction service:** *(Important: on the Host only)*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/system/limit-speed-100m.service
    [Unit]
    Description=Limit end0 advertisement to 100Mbps for Audio Purity
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=oneshot
    ExecCondition=/usr/bin/ip link show end0
    # Enable Auto-Neg but strictly limit advertisement to 100Mbps/Full
    ExecStart=/usr/bin/ethtool -s end0 speed 100 duplex full autoneg on
    RemainAfterExit=yes

    [Install]
    WantedBy=multi-user.target
    EOT
    ```

2.  **Enable and start the service:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now limit-speed-100m.service
    ```

### Step 2: Flag the Target (For QA)

To ensure the **Target QA Script** knows to validate this specific configuration, create a marker file on the Target:

```bash
sudo touch /etc/diretta-100m
```

>
>
> -----
>
> ### ✅ Checkpoint: Verify Network Configuration
>
> Your dedicated network link is now configured for "Purist" 100Mbps operation. To verify that the Host service is active and the Target has correctly negotiated the speed (detected via the marker file), please return to [**Appendix 5**](#14-appendix-5-system-health-checks) and run the universal **System Health Check** command on both the Host and the Target.
>
> -----
