#!/bin/bash

printf "\nDiretta Transmissions\n"
grep -Ee '(InfoCycle|CycleTime)' /opt/diretta-alsa/setting.inf

printf "\nLink State\n"
sudo ethtool end0 | grep -Ee '(Duplex|Speed):'

printf "\nPurist Mode Flag State\n"
if [ -e /home/audiolinux/purist-mode-webui/super_purist.flag ]; then
  echo "SET"
else
  echo "CLEARED"
fi
