#!/bin/bash

source ~/.cache/wal/colors.sh

cat >~/.config/mako/config <<EOF
background-color=${color0}cc
text-color=${foreground}ff
border-color=${color4}ff

border-size=2
border-radius=10
padding=12
default-timeout=5000
font=JetBrainsMono Nerd Font 11
EOF

makoctl reload
