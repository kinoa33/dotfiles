#!/bin/bash
cava -p ~/.config/cava/waybar.ini | while read -r line; do
    bar=""
    for char in $(echo "$line" | fold -w1); do
        case $char in
            0) bar+="▁" ;; 1) bar+="▂" ;; 2) bar+="▃" ;;
            3) bar+="▄" ;; 4) bar+="▅" ;; 5) bar+="▆" ;;
            6) bar+="▇" ;; 7) bar+="█" ;;
        esac
    done
    echo "$bar"
done
