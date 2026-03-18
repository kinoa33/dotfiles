#!/bin/bash

DIR="$HOME/Pictures/wallpapers"

wall=$(ls "$DIR" | wofi --dmenu)

if [ -n "$wall" ]; then
    wal -i "$DIR/$wall"
    swww img "$DIR/$wall"
    kill -USR1 $(pgrep kitty)
fi
