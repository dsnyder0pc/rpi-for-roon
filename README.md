# Raspberry Pi to Roon Network Bridge

## Basics for IR support on a Raspberry Pi
These are my notes for turning a Raspberry Pi running Raspberry Pi OS into a Roon network bridge, complete with support for the Flirc USB IR Receiver
https://flirc.tv/products/flirc-usb-receiver

The IR receiver allows the Raspberry Pi to receive events from a an IR remote control with a 5-way controller plus the "Back" button. This adds support for the following commands:
- KEY_UP
- KEY_DOWN
- KEY_LEFT
- KEY_RIGHT
- KEY_ENTER
- KEY_ESC

These commands can be mapped to actions applied to a specific Roon zone, giving you the ability to use almost any IR remote control with a 5-way controller to implement Play/Pause/Skip/Stop plus volume Up/Down

This works by first programming the Flirc USB with these six IR codes from your remote. You'll use software from the "Downloads" page on the flirc website above.

After programming the Flirc USB (typically using a Windows or macOS PC), you'll move it to the Raspberry Pi. To verify that all is working as expected, run these commands:
```
sudo apt install -y evtest
evtest
```

The `evtest` command will present you with a menu of devices from which it can monitor events. You should see a "Flirc" device listed. Select that one by entering the corresponding number. Next, test the 5-way controller and back buttons on your remote. You should see separate "press" and "release" events for each button printed on the screen. If you have all of this working, you're ready to proceed. If not, you can still set up Roon Bridge, but you won't have IR remote control support.

## Install the latest Python via pyenv
```
sudo apt update && sudo apt upgrade -y
sudo apt install -y git build-essential autoconf automake libtool zlib1g-dev libbz2-dev liblzma-dev libexpat1-dev libffi-dev libssl-dev libncurses5-dev libncursesw5-dev libreadline-dev uuid-dev libdb-dev libgdbm-dev libsqlite3-dev
curl -fsSL https://pyenv.run | bash
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

PYVER=$(pyenv install --list | grep '  3[0-9.]*$' | tail -n 1)
pyenv install $PYVER
pyenv global $PYVER
pyenv versions
```

## Install a few development tools in case we need them later
```
sudo apt install -y vim shellcheck tmux mosh codespell
mkdir -p ~/.vim/pack/git-plugins/start
git clone --depth 1 https://github.com/dense-analysis/ale.git ~/.vim/pack/git-plugins/start/ale
```

## Install Roon Bridge
```
curl -LO https://download.roonlabs.net/builds/roonbridge-installer-linuxarmv8.sh
sudo bash ./roonbridge-installer-linuxarmv8.sh 
```

## Prepare and patch Sebastian Mangels' roon-ir-remote software
```
git clone https://github.com/smangels/roon-ir-remote.git
cat <<'EOT' > roon-ir-remote.patch
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

## Create a config file for your Roon environment
To do this, it's important that you provide values to the two variables to match your environment and Roon zone:
```
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

## Prepare and test roon-ir-remote
```
cd roon-ir-remote
patch -p1 roon-ir-remote.patch
pyenv virtualenv roon-ir-remote
pyenv activate roon-ir-remote
pip3 install --upgrade pip pylint pytest
pip3 install -r requirements.txt

python roon_remote.py
```

The first time the program tries to connec to your Roon Server, it will wait for you to authorize the extension. You'll do this on the Extensions tab of Roon Settings. If this fails, just type CTRL-C and try running it again:

```
python roon_remote.py
```

Play some music in Roon and test the 5-way controller to make sure things are working. You should be able to control the volume (if your zone supports it), skip to the next and previous track, and start/stop playback. When you are finished testing, type CTRL-C.

## Create a systemd service for roon-ir-remote so that it runs in the background
```
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

## Profit!
