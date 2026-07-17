#!/bin/bash

cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
mem=$(free | awk '/Mem/ {printf("%.0f"), $3/$2 * 100.0}')
time=$(date +"%H:%M")

echo "{\"cpu\": \"$cpu\", \"memory\": \"$mem\", \"time\": \"$time\"}"
