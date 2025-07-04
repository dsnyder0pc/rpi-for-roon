# Building a Dedicated Diretta Link with AudioLinux on Raspberry Pi

This guide provides comprehensive, step-by-step instructions for configuring two Raspberry Pi devices as a dedicated Diretta Host and Diretta Target. This setup uses a direct, point-to-point Ethernet connection between the two devices for the ultimate in network isolation and audio performance.

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
9.  [Appendix: Optional IR Remote Control Setup](#9-appendix-optional-ir-remote-control-setup)

---

### 1. Prerequisites

#### Hardware

A complete bill of materials is provided below. While other parts can be substituted, using these specific components improves the chances of a successful build.

**Core Components (from [pishop.us](https://www.pishop.us/) or similar supplier):**
* 2 x [Raspberry Pi 4 Model B/4GB](https://www.pishop.us/product/raspberry-pi-4-model-b-4gb/)
* 2 x Aluminum Heatsink for Raspberry Pi 4B (3-Pack) (check the box to add heatsinks on the PRi 4 producet page)
* 2 x [MicroSD Card Extreme Pro - 32 GB](https://www.pishop.us/product/microsd-card-extreme-pro-32-gb-class-10-blank/)
* 2 x [Raspberry Pi 4 Case, Red/White](https://www.pishop.us/product/raspberry-pi-4-case-red-white/)
* 2 x [Raspberry Pi 45W USB-C Power Supply - White](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)
* 1 x [Micro-HDMI to Standard HDMI (A/M), 1m Cable, White](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Raspberry Pi Official Keyboard - Red/White](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Additional Networking Components:**
* 1 x [Cable Matters USB 3.0 to Ethernet Adapter](https://www.amazon.com/dp/B00AQM8586) (for the Diretta Host)
* 1 x [Short CAT6 Ethernet Patch Cable](https://www.amazon.com/dp/B00AJHCAPC) (for the point-to-point link)

**Required Audio Component:**
* 1 x USB DAC

**Optional Upgrades:**
* [iFi Audio iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (to provide clean power to the Diretta Target)
* [Flirc USB IR Receiver and Remote](https://www.amazon.com/gp/product/B0DHG99WLJ/) (to add remote control capabilities to the Diretta Host)

#### Software & Licensing Costs

* **AudioLinux:** An "Unlimited" license is recommended, which is currently **$139**. This allows for installation on multiple devices within the same location.
* **Diretta Target:** A license is required for the Diretta Target device and currently costs **100 Euros**.
    * **CRITICAL:** This license is locked to the specific hardware of the Raspberry Pi it is purchased for. It is essential that you perform the final licensing step on the exact hardware you intend to use permanently.
    * Diretta may offer a one-time replacement license for hardware failure within the first two years (please verify terms at time of purchase). If you change the hardware for any other reason, a new license must be purchased.

### 2. Initial Image Preparation

1.  **Purchase and Download:** Obtain the AudioLinux image from the official website. You will receive a link to download the `.img.gz` file.
2.  **Flash the Image:** Use your preferred imaging tool to write the downloaded AudioLinux image to **both** microSD cards.
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

The default user is `audiolinux` with password `audiolinux0`.

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

It's good security practice to create your own user and disable the default one.

```bash
# Create the new user (e.g., 'dsnyder')
sudo useradd -m -G realtime,video,audio,wheel -s /bin/bash dsnyder

# Set a strong password for the new user
sudo passwd dsnyder
```

> **Note:** We add the user to the `wheel` group for `sudo` access, and other groups like `realtime` and `audio` for necessary system permissions.

#### 3.5. Configure Passwordless Sudo

For convenience, you can allow your new user to run `sudo` commands without a password.

1.  Run `sudo visudo`.
2.  Find the line `## Same thing without a password`.
3.  Uncomment the line below it by removing the `#` prefix. It should look like this:
    ```
    ## Same thing without a password
    %wheel ALL=(ALL) NOPASSWD: ALL
    ```
4.  Save and exit the editor.

#### 3.6. Secure the Default User

Remove the default `audiolinux` user from the `wheel` group to revoke its `sudo` privileges.

1.  Edit the group file: `sudo vi /etc/group`
2.  Find the line for the `wheel` group: `wheel:x:998:audiolinux,dsnyder`
3.  Remove `audiolinux` from this line: `wheel:x:998:dsnyder`
4.  Save and exit.

**At this point, reboot the device (`sudo reboot`). Log back in with your new user account before proceeding.**

### 4. System Updates (Perform on Both Devices)

#### 4.1. Workaround for Pacman Update Issue

A known issue can prevent the system from updating due to conflicting NVIDIA firmware files (even though the RPi doesn't use them). Move these files before updating.

```bash
sudo mv -v /usr/lib/firmware/nvidia/ad10[3467] /root/
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

    *File: `sudo vi /etc/systemd/network/end0.network`*
    ```ini
    [Match]
    Name=end0

    [Network]
    Address=172.20.0.1/24
    ```

    *File: `sudo vi /etc/systemd/network/enp.network`*
    ```ini
    [Match]
    Name=enp*

    [Network]
    DHCP=yes
    DNSSEC=no
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

*File: `sudo vi /etc/systemd/network/end0.network`*
```ini
[Match]
Name=end0

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=172.16.8.1
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

2.  **Reboot Both Devices:** For a clean start, `sudo reboot` both the Host and Target.

3.  **Configure Roon:**
    * Open Roon on your control device.
    * Go to `Settings` -> `Audio`.
    * Under the "Diretta" section, you should see your device. The name will be based on your DAC.
    * Click `Enable`, give it a name, and you are ready to play music!

Your dedicated Diretta link is now fully configured for pristine, isolated audio playback.

### 9. Appendix: Optional IR Remote Control Setup

This appendix provides instructions for installing and configuring the optional Flirc USB IR receiver on the **Diretta Host**. This will allow you to control Roon playback (Play/Pause, Next/Previous Track) using a standard infrared remote via a Python script that directly reads the device events.

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

#### Step 2: Install Dependencies and Clone the Control Script

On the **Diretta Host**, we need to install the tools required to run the Python control script. AudioLinux includes the `yay` helper, which simplifies this process.

```bash
# Install git, python-pip, python-evdev, and evtest
yay -S git python-pip python-evdev evtest
```

Next, clone the repository containing the control script.

```bash
# Clone into your home directory
cd ~
git clone [https://github.com/dsnyder0pc/rpi-for-roon.git](https://github.com/dsnyder0pc/rpi-for-roon.git)
```

Finally, install the Python dependencies for the script. Since we are not using a virtual environment, the packages must be installed globally using `sudo`.

```bash
cd rpi-for-roon
sudo pip install -r requirements.txt
```

#### Step 3: Authorize the Script with Roon

The control script needs to be authorized as an extension within Roon.

1.  Run the script once manually from your home directory (`~/rpi-for-roon`).
    ```bash
    python roon_remote.py
    ```
2.  Go to your Roon desktop client or tablet app.
3.  Navigate to `Settings` -> `Extensions`.
4.  You should see an "IR Remote" extension asking for authorization. Click `Enable`.
5.  The script will save an authorization token to `~/rpi-for-roon/roon_api.token`. You can now stop the script by pressing `Ctrl+C`.

#### Step 4: Create and Enable the Systemd Service

To make the script run automatically on boot, we will create a `systemd` service.

1.  **Identify the Flirc device path:** Run `sudo evtest`. It will list all input devices. Find the one corresponding to the Flirc receiver and note its event path (e.g., `/dev/input/event3`). Press `Ctrl+C` to exit.

2.  **Create the service file:**
    ```bash
    sudo vi /etc/systemd/system/roon-remote.service
    ```

3.  **Add the following content.** Be sure to replace `dsnyder` with your actual username and `/dev/input/eventX` with the correct device path you found in the previous step.

    ```ini
    [Unit]
    Description=Roon IR Remote Control Service
    After=network-online.target

    [Service]
    Type=simple
    User=dsnyder
    WorkingDirectory=/home/dsnyder/rpi-for-roon
    ExecStart=/usr/bin/python roon_remote.py --device /dev/input/eventX --token /home/dsnyder/rpi-for-roon/roon_api.token
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

4.  **Enable and start the service:**
    ```bash
    sudo systemctl enable --now roon-remote.service
    ```

Your IR remote should now be able to control Roon playback. You can check the status of the service at any time with `systemctl status roon-remote.service`.
