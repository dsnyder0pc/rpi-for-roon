# Building a Dedicated Diretta Link with AudioLinux on Raspberry Pi

This guide provides comprehensive, step-by-step instructions for configuring two Raspberry Pi devices as a dedicated Diretta Host and Diretta Target. This setup uses a direct, point-to-point Ethernet connection between the two devices for the ultimate in network isolation and audio performance.

If you are located in the US, expect to pay around $432 in total (including tax and shipping) to complete this build:
- Hardware ($245)
- One year AudioLinux subscription ($69)
- Diretta Target license ($118)

However, I highly recommend the remote control, which adds $63, bringing the total to **$495.**

The **Diretta Host** will connect to your main network (for Roon Core, etc.) and will also act as a gateway for the Target. The **Diretta Target** will connect only to the Host and your USB DAC.

## Table of Contents
1.  [Prerequisites](#1-prerequisites)
2.  [Initial Image Preparation](#2-initial-image-preparation)
3.  [Core System Configuration (Perform on Both Devices)](#3-core-system-configuration-perform-on-both-devices)
4.  [System Updates (Perform on Both Devices)](#4-system-updates-perform-on-both-devices)
5.  [Point-to-Point Network Configuration](#5-point-to-point-network-configuration)
6.  [Convenient & Secure SSH Access](#6-convenient--secure-ssh-access)
7.  [Diretta Software Installation & Configuration](#7-diretta-software-installation--configuration)
8.  [Final Steps & Roon Integration](#8-final-steps--roon-integration)
9.  [Appendix 1: Optional IR Remote Control Setup](#9-appendix-1-optional-ir-remote-control-setup)
10.  [Appendix 2: Optional Argon One IR Remote Setup](#10-appendix-2-optional-argon-one-ir-remote-setup)
11. [Appendix 3: ARGON One Fan Control](#11-appendix-3-argon-one-fan-control)

---

### 1. Prerequisites

#### Hardware

A complete bill of materials is provided below. While other parts can be substituted, using these specific components improves the chances of a successful build.

#### About Diretta and the Raspberry Pi 5
Although the Raspberry Pi 5 is often mentioned within the context of Diretta, Energy Efficient Ethernet (EEE), also known as IEEE 802.3az, can *not* be disabled on the RPi5. EEE can be a significant problem when using the Diretta Protocol because Diretta is highly sensitive to timing and packet loss. It relies on consistent and predictable data flow between the Host (sending side) and Target (receiving side) to optimize audio quality. Therefore, until there's a hardware change or firmware fix, the RPi5 generally is not suitable for this build.

However, it _may_ be possible, and even slightly advantageous, to use a RPi5 for the Diretta Target as long as the Diretta Host is a RPi4. My observation is that EEE in AudioLinux is disabled by default on the RPi4. When the two are directly connected, the RPi5 will see that its link partner (the RPi4) is not offering EEE, and therefore the entire link will be established without EEE being enabled.

**Core Components (from [pishop.us](https://www.pishop.us/) or similar supplier):**
* 2 x [Raspberry Pi 4 Model B/4GB](https://www.pishop.us/product/raspberry-pi-4-model-b-4gb/)
* 2 x Aluminum Heatsink for Raspberry Pi 4B (3-Pack) (check the box to add heatsinks on the PRi 4 producet page)
* 2 x [Raspberry Pi 4 Case, Red/White](https://www.pishop.us/product/raspberry-pi-4-case-red-white/)
* 2 x [MicroSD Card Extreme Pro - 32 GB](https://www.pishop.us/product/microsd-card-extreme-pro-32-gb-class-10-blank/)
* 2 x [Raspberry Pi 45W USB-C Power Supply - White](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Required Networking Components:**
* 1 x [Plugable USB3 to Ethernet Adapter](https://www.amazon.com/dp/B00AQM8586) (for the Diretta Host)
* 1 x [Short CAT6 Ethernet Patch Cable](https://www.amazon.com/Cable-Matters-Ethernet-Patch-White/dp/B0CP9WYXKS/) (for the point-to-point link)

**Optional, but helpful for troubleshooting:**
* 1 x [Micro-HDMI to Standard HDMI (A/M), 2m Cable, White](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Raspberry Pi Official Keyboard - Red/White](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Optional Upgrades:**
* 1 x [Flirc USB IR Receiver and Remote](https://www.amazon.com/gp/product/B0DHG99WLJ/) (to add remote control capabilities to the Diretta Host)
* 2 x [Argon ONE V2 Aluminum Case for Raspberry Pi 4](https://www.amazon.com/Argon-Raspberry-Aluminum-Heatsink-Supports/dp/B07WP8WC3V/)
* 1 x [AudioQuest Forest Ethernet Cable 0.75 M](https://www.amazon.com/AudioQuest-RJ-Forest-Ethernet-0-75m/dp/B0073H82U8/)
* 1 x [iFi Audio iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (to provide clean power to the Diretta Target)
* 1 x [iFi LAN iSilencer](https://www.amazon.com/iFi-LAN-iSilencer-Electrical-Ethernet/dp/B0BV72SW8V/) (LAN filtering for the Diretta Target)

**Required Audio Component:**
* 1 x USB DAC or DDC

**Required Build Tools:**
* Laptop or desktop PC running Linux, macOS, or Microsoft Windows with [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* An SD or microSD card reader
* An HDMI TV or display (optional, but useful for troubleshooting)

#### Software & Licensing Costs

* **AudioLinux:** An "Unlimited" license is recommended for enthusiasts, is currently **$139**. However, it's fine to get started with a one year subscription, currently **$69**. Both options allow for installation on multiple devices within the same location.
* **Diretta Target:** A license is required for the Diretta Target device and currently costs **100 Euros**.
    * **CRITICAL:** This license is locked to the specific hardware of the Raspberry Pi it is purchased for. It is essential that you perform the final licensing step on the exact hardware you intend to use permanently.
    * Diretta may offer a one-time replacement license for hardware failure within the first two years (please verify terms at time of purchase). If you change the hardware for any other reason, a new license must be purchased.

### 2. Initial Image Preparation

1.  **Purchase and Download:** Obtain the AudioLinux image from the official website. You will receive a link to download the `.img.gz` file.
2.  **Flash the Image:** Use your preferred imaging tool (e.g., [balenaEtcher](https://etcher.balena.io/)) to write the downloaded AudioLinux image to **both** microSD cards.
    > **Note:** The AudioLinux image is a direct disk dump, not a compressed installer. As a result, the image file is quite large, and the flashing process can be unusually long. Expect it to take up to 15 minutes per card, depending on the speed of your microSD card and reader.

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

#### 3.1. Regenerate the Machine ID

The `machine-id` is a unique identifier for the OS installation. It **must** be different for each device.

```bash
# On each device, run the following commands:
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
```

After running these commands, you can verify the new, unique ID with `cat /etc/machine-id`.

#### 3.2. Set Unique Hostnames

Set a clear hostname for each device to easily identify them.

```bash
# On the Diretta Host
sudo hostnamectl set-hostname diretta-host

# On the Diretta Target
sudo hostnamectl set-hostname diretta-target
```

#### 3.3. Set Your Timezone

```bash
# Example for Phoenix, USA. Find your timezone with 'timedatectl list-timezones'
sudo timedatectl set-timezone America/Phoenix
```

#### 3.4. Create a New Administrative User

Optional, but if you wish, you may create a new administrative user for yourself. For example, I'm using `dsnyder`

```bash
# Create the new user (e.g., 'dsnyder')
sudo useradd -m -G input,realtime,video,audio -s /bin/bash dsnyder

# Set a strong password for the new user
sudo passwd dsnyder
```

> **Note:** We add the user to the `wheel` group for `sudo` access, and other groups like `realtime` and `audio` for necessary system permissions.

#### 3.5. Configure Passwordless Sudo

For convenience, you can allow your new user to run `sudo` commands without a password.

```
printf 'dsnyder\t\tALL = (ALL) NOPASSWD: ALL\n' | sudo tee /etc/sudoers.d/dsnyder
```

**At this point, reboot the device (`sudo reboot`). Log back in with your new user account before proceeding.**

Repeat the above steps for the second Raspberry Pi once you're able to login to the first one.

### 4. System Updates (Perform on Both Devices)

#### 4.1. Workaround for Pacman Update Issue

A [known issue](https://archlinux.org/news/linux-firmware-2025061312fe085f-5-upgrade-requires-manual-intervention/) can prevent the system from updating due to conflicting NVIDIA firmware files (even though the RPi doesn't use them). To progress with the system upgrade, first remove `linux-firmware`, then reinstall it as part of the upgrade:

```bash
sudo pacman -Rdd linux-firmware
sudo pacman -Syu linux-firmware
```

#### 4.2. Run System and Menu Updates

Use the AudioLinux menu system to perform all updates.

1.  Run `menu` in the terminal.
2.  Select **INSTALL/UPDATE menu**.
3.  On the next screen, select **UPDATE system** and let the process complete.
4.  After the system update finishes, select **Update menu** from the same screen to get the latest version of the AudioLinux scripts.

### 5. Point-to-Point Network Configuration

In this section, we will create the network configuration files that will activate the dedicated private link. To avoid needing a physical keyboard and monitor (console access), we will perform these steps while both devices are still connected to your main LAN and accessible via SSH.

#### 5.1. Pre-configure the Diretta Host

1.  **Enable IP Forwarding:**
    ```bash
    # Enable it for the current session
    sudo sysctl -w net.ipv4.ip_forward=1
    
    # Make it permanent across reboots
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

2.  **Create Network Files:**
    Create the following two files on the **Diretta Host**. The `end0.network` file sets the static IP for the future point-to-point link. The `enp.network` file ensures the USB Ethernet adapter continues to get an IP from your main LAN.

    *File: `sudo nano /etc/systemd/network/end0.network`*
    ```ini
    [Match]
    Name=end0

    [Network]
    Address=172.20.0.1/24
    ```

    *File: `sudo nano /etc/systemd/network/enp.network`*
    ```ini
    [Match]
    Name=enp*

    [Network]
    DHCP=yes
    DNSSEC=no
    ```

    **Important:** Remove the old en.network file if present:
    ```
    sudo rm -fv /etc/systemd/network/en.network
    ```

    Add an /etc/hosts entry for the Diretta Target:
    ```
    printf "172.20.0.2\tdiretta-target target\n" | sudo tee -a /etc/hosts
    ```

3.  **Configure Network Address Translation (NAT):**
    ```bash
    # Add the firewall rule. The -o enp+ will match your USB adapter.
    sudo iptables -t nat -A POSTROUTING -s 172.20.0.0/24 -o enp+ -j MASQUERADE
    
    # Save the rule to make it permanent
    sudo iptables-save | sudo tee /etc/iptables/iptables.rules
    sudo systemctl enable iptables.service
    ```

#### 5.2. Pre-configure the Diretta Target

On the **Diretta Target**, create the `end0.network` file. This configures its static IP and tells it to use the Diretta Host as its gateway for all internet traffic.

*File: `sudo nano /etc/systemd/network/end0.network`*
```ini
[Match]
Name=end0

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=172.16.8.1
```

Add an /etc/hosts entry for the Diretta Host:
```
printf "172.20.0.1\tdiretta-host host\n" | sudo tee -a /etc/hosts
```

**Important:** Remove the old en.network file if present:
```
sudo rm -fv /etc/systemd/network/en.network
```

#### 5.3. The Physical Connection Change

> **Warning:** Double-check the contents of the files you just created. A typo could make a device inaccessible after rebooting, requiring a console session or re-flashing the SD card to fix.

1.  Once you have verified the files, perform a clean shutdown of **both** devices:
    ```bash
    sudo sync; sudo poweroff
    ```
2.  Disconnect both devices from your main LAN switch/router.
3.  Connect the **onboard Ethernet port** of the Diretta Host directly to the **onboard Ethernet port** of the Diretta Target using a single Ethernet cable.
4.  Connect the **USB-to-Ethernet adapter** on the Diretta Host to your main LAN switch/router.
5.  Power on both devices.

Upon booting, they will automatically use the new network configurations. You should now be able to ping the Target from the Host (`ping 172.20.0.2`) and ping public websites from the Target (`ping google.com`) to verify the connection is working.

### 6. Convenient & Secure SSH Access

#### 6.1. The `ProxyJump` Requirement

Now that the network is configured, the **Diretta Target** is on an isolated network (`172.20.0.0/24`) and cannot be reached directly from your main LAN. The only way to access it is to "jump" through the **Diretta Host**.

The `ProxyJump` directive in your local SSH configuration is the standard and required method to achieve this.

1.  **Configure SSH Aliases:**
    On your local computer (e.g., your laptop), edit the file `~/.ssh/config`. This configuration tells SSH how to reach the Target by first connecting to the Host.

    ```
    Host diretta-host host
        HostName <diretta-host-lan-ip>
        User dsnyder

    Host diretta-target target
        HostName 172.20.0.2
        User dsnyder
        ProxyJump diretta-host
    ```
    *(Replace `<diretta-host-lan-ip>` with the actual IP of the Host on your LAN, and `dsnyder` with your username.)*

With this configuration in place, SSH handles the connection routing automatically when you try to connect to `diretta-target`.

#### 6.2. Recommended: Secure Authentication with SSH Keys

While you can use passwords over the proxied connection, the most secure and convenient method is public key authentication. This uses a passphrase-protected SSH key managed by an agent (`ssh-agent`), eliminating the need to re-enter your password for every connection.

**On your local computer:**

1.  **Create an SSH Key (if you don't have one):**
    It's best practice to use a modern algorithm like `ed25519`. When prompted, enter a strong, memorable passphrase.
    ```bash
    ssh-keygen -t ed25519 -C "your_email@example.com"
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
    ssh-copy-id diretta-host
    ssh-copy-id diretta-target
    ```

You can now SSH to both devices (`ssh diretta-host`, `ssh diretta-target`) without a password, securely authenticated by your SSH key.

### 7. Diretta Software Installation & Configuration

#### 7.1. On the Diretta Target

1.  Connect your USB DAC to one of the USB ports on the **Diretta Target** and ensure the DAC is powered on.
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

#### 7.2. On the Diretta Host

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
    * Choose **1) Install/update** to install the software.
    * Choose **2) Enable/Disable Diretta daemon** and enable it.
    * Choose **3) Set Ethernet interface**. It is critical to select the interface for the point-to-point link.
        ```
        ?3
        Your available Ethernet interfaces are: end0  enp1s0u1u2
        Please type the name of your preferred interface:
        end0
        ```
    * Choose **4) Edit configuration** only if you need to make advanced changes. The previous steps should be sufficient.

### 8. Final Steps & Roon Integration

1.  **Install Roon Bridge (on Host):** If you use Roon, perform the following steps on the **Diretta Host**:
    * Run `menu`.
    * Select **INSTALL/UPDATE menu**.
    * Select **INSTALL/UPDATE Roonbridge**.
    * The installation will proceed, and the Roon Bridge service will be enabled and started automatically upon completion.

2.  **Minimize disk I/O on the Diretta Host and Target:** (optional but recommended for optimal performance)
    * Chang `#Storage=auto` to `Storage=volatile` in `/etc/systemd/journald.conf`

3.  **Reboot Both Devices:** For a clean start, `sudo reboot` both the Host and Target.

4.  **Configure Roon:**
    * Open Roon on your control device.
    * Go to `Settings` -> `Audio`.
    * Under the "Diretta" section, you should see your device. The name will be based on your DAC.
    * Click `Enable`, give it a name, and you are ready to play music!

Your dedicated Diretta link is now fully configured for pristine, isolated audio playback.

### 9. Appendix 1: Optional IR Remote Control Setup

This appendix provides instructions for installing and configuring the optional Flirc USB IR receiver on the **Diretta Host**. This will allow you to control Roon playback (Play/Pause, Next/Previous Track) using a standard infrared remote via a Python script that directly reads the device events.

To get started, you'll need to purchase the Flirc USB IR Receiver. Here's a link to purchase that also includes the required downloads for configuration:

[https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

This IR receiver allows the Raspberry Pi to receive events from an IR remote control with a 5-way controller plus the "Back" button. This adds support for the following commands:

  - KEY\_UP
  - KEY\_DOWN
  - KEY\_LEFT
  - KEY\_RIGHT
  - KEY\_ENTER
  - KEY\_ESC

This works by first programming the Flirc USB with these six IR codes from your remote. You'll use software from the "Downloads" page on the flirc website above.

#### Step 1: Program the Flirc Device

The Flirc device needs to be programmed to translate IR signals from your remote into specific keyboard presses. This must be done on a desktop computer (Windows/macOS/Linux) using the Flirc GUI software, available from the [Flirc website](https://flirc.tv/downloads).

1.  Plug the Flirc USB receiver into your desktop computer.
2.  Open the Flirc GUI software.
3.  Go to `Controllers` and select `Full Keyboard`.
4.  Program the following keys, which the control script will listen for:
    * Click the `Play/Pause` key in the GUI, then press the corresponding button on your physical remote.
    * Click the `Stop` key in the GUI, then press the corresponding button on your remote.
    * Click the `Next Track` key in the GUI, then press the corresponding button on your remote.
    * Click the `Previous Track` key in the GUI, then press the corresponding button on your remote.
5.  Once programmed, close the software and plug the Flirc USB receiver into the **Diretta Host**.

#### Step 2: Test the Flirc USB on your Raspberry Pi

After programming the Flirc USB (typically using a Windows or macOS PC), you'll move it to the Raspberry Pi. To verify that all is working as expected, SSH into your Raspberry Pi and run these commands:

```bash
sudo pacman -S --noconfirm evtest
evtest
```

The `evtest` command will present you with a menu of devices from which it can monitor events. You should see a "Flirc" device listed. Select that one by entering the corresponding number. Next, test the 5-way controller and back buttons on your remote. You should see separate "press" and "release" events for each button printed on the screen.

-----

#### Step 3: Install the latest Python via pyenv

This solution requires a modern Python installation. First, install the necessary build dependencies for `pyenv` and Python. The `base-devel` group in Arch Linux provides most of the essential tools like `gcc` and `make`.

```bash
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite
curl -fsSL https://pyenv.run | bash
```

Next, add `pyenv` to your shell's configuration file. The original instructions use `.bashrc`, which will work for the `bash` shell.

```bash
cat <<'EOT'>> ~/.bashrc

# Load pyenv automatically by appending
# the following to
# ~/.bash_profile if it exists, otherwise ~/.profile (for login shells)
# and ~/.bashrc (for interactive shells) :

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

# Restart your shell for the changes to take effect.

# Load pyenv-virtualenv automatically by adding
# the following to ~/.bashrc:

eval "$(pyenv virtualenv-init -)"
EOT

. ~/.bashrc
```

Now, install and set the latest stable version of Python.

```bash
PYVER=$(pyenv install --list | grep '  3[0-9.]*$' | tail -n 1)
pyenv install $PYVER
pyenv global $PYVER
pyenv versions
```

-----

#### Step 4: Install a few development tools in case we need them later

Install `vim` and other useful development tools. Since **`shellcheck`** is in the AUR, we'll use **`yay`** to install it. If you don't have `yay` installed, you'll need to install it first.

```bash
# Install tools from the official repositories
sudo pacman -S --noconfirm vim tmux mosh codespell

# Install shellcheck from the AUR using yay
yay -S --noconfirm shellcheck

# Set up the ALE plugin for vim
mkdir -p ~/.vim/pack/git-plugins/start
git clone --depth 1 https://github.com/dense-analysis/ale.git ~/.vim/pack/git-plugins/start/ale
```

-----

#### Step 5: Prepare and patch Sebastian Mangels' roon-ir-remote software

This process of cloning the repository and creating the patch file is unchanged.

```bash
git clone https://github.com/smangels/roon-ir-remote.git
cat <<'EOT' > roon-ir-remote/roon-ir-remote.patch
diff --git a/roon_remote.py b/roon_remote.py
index 64a8317..db5ead8 100644
--- a/roon_remote.py
+++ b/roon_remote.py
@@ -3,18 +3,18 @@ Implement a Roon Remote extension that reads keyboard events
 from a FLIRC device and converts those events into transport
 commands towards a certain _Zone_ in Roon.
 """
-# !/usr/bin/python
+# !/usr/bin/env python
 import logging
 import signal
 import sys
 from pathlib import Path
 
 import evdev
-from evdev import InputDevice
+from evdev import InputDevice, ecodes, categorize
 
 from app import RoonController, RoonOutput, RemoteConfig, RemoteConfigE, RemoteKeycodeMapping, RoonControllerE
 
-logging.basicConfig(level=logging.DEBUG,
+logging.basicConfig(level=logging.WARNING,
                     format='%(asctime)s %(levelname)s %(module)s: %(message)s')
 logger = logging.getLogger('roon_remote')
 
@@ -56,31 +56,33 @@ def monitor_remote(zone: RoonOutput, dev: InputDevice, mapping: RemoteKeycodeMap
             # ignore everything that is not KEY_DOWN
             continue
 
-        # logging.debug(str(categorize(event)))
+        event_name = ecodes.KEY[event.code]
+        logging.debug(str(categorize(event)))
         try:
-            # logging.debug("Status: {}".format('uninitialized'))
-            # logging.debug("KeyCode: {}".format(event.code))
-            if event.code in mapping.to_key_code('prev'):
+            logging.debug("Status: {}".format('uninitialized'))
+            logging.debug("KeyCode Number: {}".format(event.code))
+            logging.debug("KeyCode Name: {}".format(event_name))
+            if event_name == mapping.to_key_code('prev'):
                 zone.previous()
-            elif event.code in mapping.to_key_code('skip'):
+            elif event_name == mapping.to_key_code('skip'):
                 zone.skip()
-            elif event.code in mapping.to_key_code('stop'):
+            elif event_name == mapping.to_key_code('stop'):
                 zone.stop()
-            elif event.code in mapping.to_key_code('play_pause'):
+            elif event_name == mapping.to_key_code('play_pause'):
                 if zone.state == "playing":
                     zone.pause()
                 else:
                     zone.repeat(False)
                     zone.play()
-            elif event.code in mapping.to_key_code('vol_up'):
+            elif event_name == mapping.to_key_code('vol_up'):
                 zone.volume_up(2)
-            elif event.code in mapping.to_key_code('vol_down'):
+            elif event_name == mapping.to_key_code('vol_down'):
                 zone.volume_down(2)
-            elif event.code in mapping.to_key_code('mute'):
+            elif event_name == mapping.to_key_code('mute'):
                 zone.mute(not zone.is_muted())
-            elif event.code in mapping.to_key_code('fall_asleep'):
+            elif event_name == mapping.to_key_code('fall_asleep'):
                 zone.play_playlist('wellenrauschen')
-            elif event.code in mapping.to_key_code('play_radio'):
+            elif event_name == mapping.to_key_code('play_radio'):
                 zone.play_radio_station(station_name="Radio Paradise (320k aac)")
 
             logger.debug("Received Code: %s", repr(event.code))
EOT
```

-----

#### Step 6: Create a config file for your Roon environment

This step is also identical. Be sure to replace the placeholder values for your email and Roon zone. It's especially critical to make sure that the zone name EXACTLY matches what you see in the Roon UI for your Zone.

```bash
MY_EMAIL_ADDRESS="Put your email address here"
MY_ROON_ZONE="Enter Roon zone name here EXACTLY as it is spelled in the Roon UI"
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
        "vol_up": "KEY_UP",
        "vol_down": "KEY_DOWN"
      }
    }
  }
}
EOT
```

-----

#### Step 7: Prepare and test roon-ir-remote

These steps, which use `patch`, `pyenv`, and `pip`, are not specific to the operating system and remain the same.

```bash
cd roon-ir-remote
patch -p1 < roon-ir-remote.patch
pyenv virtualenv roon-ir-remote
pyenv activate roon-ir-remote
pip3 install --upgrade pip pylint pytest
pip3 install -r requirements.txt

python roon_remote.py
```

The first time you run the program, you will need to authorize the extension in Roon's Settings, under the "Extensions" tab.

-----

#### Step 8: Create a systemd service for roon-ir-remote so that it runs in the background

Creating a `systemd` service is standard on both Ubuntu and Arch Linux. These commands will work without any changes.

```bash
cat <<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
# This ensures the network is up before starting the service
After=network.target

[Service]
# Type simple means the script is the main process of the service
Type=simple

# Run the service as the '${LOGNAME}' user and group
User=${LOGNAME}
Group=${LOGNAME}

# Set the working directory to where your script is located
# This is the equivalent of your 'cd roon-ir-remote/' command
WorkingDirectory=/home/${LOGNAME}/roon-ir-remote

# This is the full command to execute.
# We use the ABSOLUTE PATH to the python executable within your pyenv virtual environment.
# This completely bypasses the need for 'pyenv activate'.
ExecStart=/home/${LOGNAME}/.pyenv/versions/roon-ir-remote/bin/python /home/${LOGNAME}/roon-ir-remote/roon_remote.py

# Automatically restart the service if it fails
Restart=on-failure
RestartSec=5

[Install]
# This tells systemd to start the service during the normal multi-user boot process
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable roon-ir-remote.service
sudo systemctl start roon-ir-remote.service
sudo systemctl status roon-ir-remote.service
sudo journalctl -u roon-ir-remote.service -f
```

### 10. Appendix 2: Optional Argon One IR Remote Setup

This appendix provides instructions for installing and configuring the Argon One V2/V3 case's built-in infrared receiver on the **Diretta Host**. This will allow you to control Roon playback using the Argon IR remote.

Unlike the Flirc which is a smart device that emulates a keyboard, the Argon One's receiver is connected directly to the Raspberry Pi's GPIO pins. We will use the modern kernel-level tool **`ir-keytable`** to capture IR signals and translate them into standard keyboard events that the `roon-ir-remote` script can use.

-----

#### Step 1: Enable the IR Receiver Hardware

First, you must enable the specific hardware interfaces for the Argon One case and its IR receiver.

1.  Edit your boot configuration file with a text editor:
    ```bash
    sudo nano /boot/config.txt
    ```
2.  Add the following lines to the end of the file. This enables the I2C interface for the case's fan control and activates the IR receiver on the correct GPIO pin.
    ```
    dtparam=i2c_arm=on
    dtoverlay=gpio-ir,gpio_pin=23
    ```
3.  Save the file, exit the editor, and reboot for the change to take effect.
    ```bash
    sudo reboot
    ```

-----

#### Step 2: Install IR Tools and Capture Scancodes

Next, install the necessary tools and capture the unique codes for each button on your remote.

1.  Install the `v4l-utils` package, which provides `ir-keytable`:
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```
2.  Run the `ir-keytable` test tool to see the scancodes for your remote.
    ```bash
    sudo ir-keytable -t
    ```
3.  Press each button on your remote (Up, Down, Left, Right, OK/Enter, Back, Volume Up, Volume Down). For each press, you will see output that contains the scancode. Write down the scancode for each button. For example:
    ```
    Event: time 1752715725.730574, type 4 (EV_MSC), code 4 (MSC_SCAN), value ca
    ```
    In this example, the scancode is `0xca`. Press `Ctrl+C` when you are finished.

-----

#### Step 3: Create the Keymap File

This file maps the scancodes you captured to standard Linux key names. The example below uses the known scancodes for the Argon remote.

1.  Create a new keymap file:
    ```bash
    sudo nano /etc/rc_keymaps/argon.toml
    ```
2.  Paste the following content into the file. This configuration ensures that the arrow keys and volume keys send distinct signals.
    ```toml
    # /etc/rc_keymaps/argon.toml
    # Keymap for the Argon IR Remote

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
    ```
3.  Save the file and exit the editor.

-----

#### Step 4: Create a Systemd Service to Load the Keymap

To ensure your keymap is loaded automatically on every boot, create a simple `systemd` service.

1.  Create a new service file:
    ```bash
    sudo nano /etc/systemd/system/ir-keymap.service
    ```
2.  Paste the following content into the file. This defines a one-shot service that loads your keymap after the system boots.
    ```ini
    [Unit]
    Description=Load custom IR keymap
    After=multi-user.target

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/bin/ir-keytable -c -p nec -w /etc/rc_keymaps/argon.toml

    [Install]
    WantedBy=multi-user.target
    ```
3.  Save the file, then enable and start your new service:
    ```bash
    sudo systemctl enable --now ir-keymap.service
    ```

-----

#### Step 5: Test the Input Device

Finally, verify that the system is correctly receiving the IR signals as keyboard presses.

1.  Install the `evtest` tool:
    ```bash
    sudo pacman -S --noconfirm evtest
    ```
2.  Run `evtest`. It will show you a list of available input devices. Choose the one that corresponds to your IR receiver (e.g., `gpio_ir_recv`).
    ```bash
    sudo evtest
    ```
3.  Press buttons on your remote. You should see "press" and "release" events for each corresponding key (`KEY_UP`, `KEY_VOLUMEUP`, etc.), confirming your setup is working perfectly.

-----

#### Step 6: Install the latest Python via pyenv

This solution requires a modern Python installation. First, install the necessary build dependencies for `pyenv` and Python. The `base-devel` group in Arch Linux provides most of the essential tools like `gcc` and `make`.

```bash
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite
curl -fsSL https://pyenv.run | bash
```

Next, add `pyenv` to your shell's configuration file. The original instructions use `.bashrc`, which will work for the `bash` shell.

```bash
cat <<'EOT'>> ~/.bashrc

# Load pyenv automatically by appending
# the following to
# ~/.bash_profile if it exists, otherwise ~/.profile (for login shells)
# and ~/.bashrc (for interactive shells) :

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

# Restart your shell for the changes to take effect.

# Load pyenv-virtualenv automatically by adding
# the following to ~/.bashrc:

eval "$(pyenv virtualenv-init -)"
EOT

. ~/.bashrc
```

Now, install and set the latest stable version of Python.

```bash
PYVER=$(pyenv install --list | grep '  3[0-9.]*$' | tail -n 1)
pyenv install $PYVER
pyenv global $PYVER
pyenv versions
```

-----

#### Step 7: Install a few development tools in case we need them later

Install `vim` and other useful development tools. Since **`shellcheck`** is in the AUR, we'll use **`yay`** to install it. If you don't have `yay` installed, you'll need to install it first.

```bash
# Install tools from the official repositories
sudo pacman -S --noconfirm vim tmux mosh codespell

# Install shellcheck from the AUR using yay
yay -S --noconfirm shellcheck

# Set up the ALE plugin for vim
mkdir -p ~/.vim/pack/git-plugins/start
git clone --depth 1 https://github.com/dense-analysis/ale.git ~/.vim/pack/git-plugins/start/ale
```

-----

#### Step 8: Prepare and patch Sebastian Mangels' roon-ir-remote software

This process of cloning the repository and creating the patch file is unchanged.

```bash
git clone https://github.com/smangels/roon-ir-remote.git
cat <<'EOT' > roon-ir-remote/roon-ir-remote.patch
diff --git a/roon_remote.py b/roon_remote.py
index 64a8317..db5ead8 100644
--- a/roon_remote.py
+++ b/roon_remote.py
@@ -3,18 +3,18 @@ Implement a Roon Remote extension that reads keyboard events
 from a FLIRC device and converts those events into transport
 commands towards a certain _Zone_ in Roon.
 """
-# !/usr/bin/python
+# !/usr/bin/env python
 import logging
 import signal
 import sys
 from pathlib import Path

 import evdev
-from evdev import InputDevice
+from evdev import InputDevice, ecodes, categorize

 from app import RoonController, RoonOutput, RemoteConfig, RemoteConfigE, RemoteKeycodeMapping, RoonControllerE

-logging.basicConfig(level=logging.DEBUG,
+logging.basicConfig(level=logging.WARNING,
                       format='%(asctime)s %(levelname)s %(module)s: %(message)s')
 logger = logging.getLogger('roon_remote')

@@ -56,31 +56,33 @@ def monitor_remote(zone: RoonOutput, dev: InputDevice, mapping: RemoteKeycodeMap
               # ignore everything that is not KEY_DOWN
               continue

-        # logging.debug(str(categorize(event)))
+        event_name = ecodes.KEY[event.code]
+        logging.debug(str(categorize(event)))
         try:
-            # logging.debug("Status: {}".format('uninitialized'))
-            # logging.debug("KeyCode: {}".format(event.code))
-            if event.code in mapping.to_key_code('prev'):
+            logging.debug("Status: {}".format('uninitialized'))
+            logging.debug("KeyCode Number: {}".format(event.code))
+            logging.debug("KeyCode Name: {}".format(event_name))
+            if event_name == mapping.to_key_code('prev'):
                 zone.previous()
-            elif event.code in mapping.to_key_code('skip'):
+            elif event_name == mapping.to_key_code('skip'):
                 zone.skip()
-            elif event.code in mapping.to_key_code('stop'):
+            elif event_name == mapping.to_key_code('stop'):
                 zone.stop()
-            elif event.code in mapping.to_key_code('play_pause'):
+            elif event_name == mapping.to_key_code('play_pause'):
                 if zone.state == "playing":
                     zone.pause()
                 else:
                     zone.repeat(False)
                     zone.play()
-            elif event.code in mapping.to_key_code('vol_up'):
+            elif event_name == mapping.to_key_code('vol_up'):
                 zone.volume_up(2)
-            elif event.code in mapping.to_key_code('vol_down'):
+            elif event_name == mapping.to_key_code('vol_down'):
                 zone.volume_down(2)
-            elif event.code in mapping.to_key_code('mute'):
+            elif event_name == mapping.to_key_code('mute'):
                 zone.mute(not zone.is_muted())
-            elif event.code in mapping.to_key_code('fall_asleep'):
+            elif event_name == mapping.to_key_code('fall_asleep'):
                 zone.play_playlist('wellenrauschen')
-            elif event.code in mapping.to_key_code('play_radio'):
+            elif event_name == mapping.to_key_code('play_radio'):
                 zone.play_radio_station(station_name="Radio Paradise (320k aac)")

             logger.debug("Received Code: %s", repr(event.code))
EOT
```

-----

#### Step 9: Create a config file for your Roon environment

This step configures the Roon script. Note that we have updated the `event_mapping` codes to match the keymap file from Step 3, so that the dedicated volume buttons control volume.

1.  Set your email and Roon Zone name. The zone name must EXACTLY match the name in the Roon UI.
    ```bash
    MY_EMAIL_ADDRESS="Put your email address here"
    MY_ROON_ZONE="Enter Roon zone name here EXACTLY as it is spelled in the Roon UI"
    ```
2.  Create the configuration file.
    ```bash
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
            "vol_down": "KEY_VOLUMEDOWN"
          }
        }
      }
    }
    EOT
    ```

-----

#### Step 10: Prepare and test roon-ir-remote

These steps, which use `patch`, `pyenv`, and `pip`, are not specific to the operating system and remain the same.

```bash
cd roon-ir-remote
patch -p1 < roon-ir-remote.patch
pyenv virtualenv roon-ir-remote
pyenv activate roon-ir-remote
pip3 install --upgrade pip pylint pytest
pip3 install -r requirements.txt

python roon_remote.py
```

The first time you run the program, you will need to authorize the extension in Roon's Settings, under the "Extensions" tab.

-----

#### Step 11: Create a systemd service for roon-ir-remote so that it runs in the background

Creating a `systemd` service is standard on both Ubuntu and Arch Linux. These commands will work without any changes.

```bash
cat <<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
# This ensures the network is up before starting the service
After=network.target

[Service]
# Type simple means the script is the main process of the service
Type=simple

# Run the service as the '${LOGNAME}' user and group
User=${LOGNAME}
Group=${LOGNAME}

# Set the working directory to where your script is located
# This is the equivalent of your 'cd roon-ir-remote/' command
WorkingDirectory=/home/${LOGNAME}/roon-ir-remote

# This is the full command to execute.
# We use the ABSOLUTE PATH to the python executable within your pyenv virtual environment.
# This completely bypasses the need for 'pyenv activate'.
ExecStart=/home/${LOGNAME}/.pyenv/versions/roon-ir-remote/bin/python /home/${LOGNAME}/roon-ir-remote/roon_remote.py

# Automatically restart the service if it fails
Restart=on-failure
RestartSec=5

[Install]
# This tells systemd to start the service during the normal multi-user boot process
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable roon-ir-remote.service
sudo systemctl start roon-ir-remote.service
sudo systemctl status roon-ir-remote.service
sudo journalctl -u roon-ir-remote.service -f
```

-----

### 11. Appendix 3: ARGON One Fan Control
If you decoded to use an ARGON One case for your Raspberry Pi, the default installer script assumes you're running a Debian O/S. However AudioLinux is based on Arch Linux, so you'll have to follow these steps instead.

#### Step 1: Skip the `argon1.sh` script in the manual
The manual says to download the argon1.sh script from download.argon40.com and pipe it to `bash`. This won't work, so skip this step and follow the steps below instead.

#### Step 2: Configure your system:
You need to enable the I2C interface, which the case uses to communicate with the Raspberry Pi. Edit `/boot/config.txt` and uncommont following line near the top:
```
dtparam=i2c_arm=on
```

Also, add the following where you see the other `dtoverlay` statements:
```
dtoverlay=argonone
```

#### Step 3: Configure `udev` permissions
```
echo 'KERNEL=="i2c-[0-9]*", MODE="0666"' | sudo tee /etc/udev/rules.d/99-i2c.rules
```

#### Step 4: Install the Argon One Package
```
yay -S argonone-c-git
```

#### Step 5: Enable the Service
```
sudo systemctl enable argononed.service
```

#### Step 6: Reboot
Finally, reboot your Raspberry Pi for all changes to take effect:
```
sudo sync; sudo reboot
```

Now, the fan will be controlled by the daemon, and the power button will have full functionality.

#### Step 7: Verify the service
```
systemctl status argononed.service
journalctl -u argononed.service -b
```

#### Step 8: Review Fan Mode and Settings:
To see the current configuration values, run the following command:
```
sudo argonone-cli --decode
```

To adjust those values, you must create a config file. Use these values to start:
```
sudo nano /etc/argononed.conf
```
Add these lines:
```
[Schedule]
temp0=55
fan0=10
temp1=60
fan1=55
temp2=65
fan2=100

[Setting]
hysteresis=3
```

Restart the service to pick up the new configuration values:
```
sudo systemctl restart argononed.service
```

Now, feel free to adjust the values as needed, following the steps above.
