#!/bin/bash

netstat -nr

printf "\nDNS\n"
if grep -q dns /etc/nsswitch.conf; then
  echo "Enabled"
else
  echo "Disabled"
fi

printf "\nChrony\n"
if chronyc sources > /dev/null 2>&1; then
  echo "Enabled"
else
  echo "Disabled"
fi

printf "\nLink State\n"
sudo ethtool end0 | grep -Ee '(Duplex|Speed):'

printf "\nPurist Mode on Boot\n"
if systemctl is-enabled --quiet purist-mode-auto.service; then
  echo "Enabled"
else
  echo "Disabled"
fi
