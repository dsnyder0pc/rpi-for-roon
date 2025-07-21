### Instructions for Tom: Updating the Purist Mode Setup

Hey Tom,

Here are the steps to update the `purist-mode` feature on your Diretta Target to the latest, most reliable version. This will fix the boot-up timing issues and simplify the setup.

Just copy and paste the large command blocks below, one at a time, into your SSH session with the Target.

#### Step 1: Clean Up the Old Setup

First, we'll revert to standard mode and completely remove the old, problematic timer and service files to ensure a clean slate.

```bash
echo "--- Step 1: Cleaning up old Purist Mode services ---"
# Revert to standard mode just in case
purist-mode --revert

# Disable and stop any old units that might exist
sudo systemctl disable --now purist-mode-auto.timer
sudo systemctl disable --now purist-mode-auto.service

# Remove the old files
sudo rm -f /etc/systemd/system/purist-mode-auto.timer
sudo rm -f /etc/systemd/system/purist-mode-auto.service

echo "✅ Old services removed."
```

#### Step 2: Update the Main `purist-mode` Script

Next, we'll download the latest version of the main script, which contains all the recent bug fixes.

```bash
echo "--- Step 2: Updating the main purist-mode script ---"
curl -Lo purist-mode https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin/
rm purist-mode
echo "✅ purist-mode script updated."
```

#### Step 3: Create the New `systemd` Services

Now, we'll create the two new, simplified service files. One ensures the system always boots into standard mode, and the other handles the delayed activation without needing a separate timer.

```bash
echo "--- Step 3: Creating the new systemd service files ---"

# Create the service to revert to standard mode on every boot
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

# Create the delayed auto-activation service
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-auto.service
[Unit]
Description=Activate Purist Mode 60 seconds after boot

[Service]
Type=oneshot
ExecStart=/bin/bash -c "sleep 60 && /usr/local/bin/purist-mode"

[Install]
WantedBy=multi-user.target
EOT

echo "✅ New service files created."
```

#### Step 4: Enable the New Services

Finally, we'll tell `systemd` about the new files and enable them to run at boot.

```bash
echo "--- Step 4: Enabling the new services ---"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
echo "✅ New services enabled."
```

#### Step 5: Update the Convenience Aliases

The aliases in your `~/.bashrc` file need to be updated to work with the new service.

1.  Open the file for editing:
    ```bash
    vi ~/.bashrc
    ```
2.  Find and **delete** the old alias block. It will look like this:
    ```bash
    # Aliases to manage the automatic Purist Mode timer
    alias purist-mode-auto-enable='...'
    alias purist-mode-auto-disable='...'
    ```
3.  Paste in this **new, corrected block** of code (usually at the end of the file):
    ```bash
    # Aliases to manage the automatic Purist Mode service
    alias purist-mode-auto-enable='echo "Enabling Purist Mode on boot..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
    alias purist-mode-auto-disable='echo "Disabling Purist Mode on boot..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
    ```
4.  Save and exit the file (in `vi`, that's `Esc` then `:wq`).
5.  Activate the new aliases in your current session:
    ```bash
    source ~/.bashrc
    ```

You're all set\! Just `sudo reboot` the Diretta Target, and everything should now be working perfectly.
