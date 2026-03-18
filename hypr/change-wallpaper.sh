#!/bin/bash

DIR="$HOME/Pictures/wallpapers"

wall=$(ls "$DIR" | wofi --dmenu)

if [ -n "$wall" ]; then
    swww img "$DIR/$wall" --transition-type wipe --transition-angle 270 --transition-duration 0.7 &
    wal -i "$DIR/$wall" -n &
    
    (sleep 0.6 && pkill waybar && waybar &) &
fi
