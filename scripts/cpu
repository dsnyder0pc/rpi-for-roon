#!/bin/bash

awk '{printf("- CPU temp : %.1f'"'"'C : %.1f'"'"'F\n", $1/1000, 32+($1/1000)*9/5)}' /sys/devices/virtual/thermal/thermal_zone0/temp
