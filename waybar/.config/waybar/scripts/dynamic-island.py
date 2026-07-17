#!/usr/bin/env python3
"""
Dynamic Island style Waybar module for Hyprland.

Default state : shows the clock (HH:MM).
On workspace switch : shows the workspace number spelled out in words
                       (e.g. "Three") for REVERT_TIMEOUT seconds, then
                       reverts back to the clock automatically.

No polling against hyprctl is used. Workspace changes are picked up
in real time via Hyprland's event socket (socket2).
"""

import os
import socket
import threading
import time
import json
import datetime

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REVERT_TIMEOUT = 2.5     # seconds the workspace name stays on screen
POLL_INTERVAL = 0.2      # internal tick used to time the revert / clock refresh
# ---------------------------------------------------------------------------

ONES = [
    "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
    "Sixteen", "Seventeen", "Eighteen", "Nineteen",
]
TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
    "Eighty", "Ninety",
]


def number_to_words(n: int) -> str:
    if n < 0:
        return number_to_words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return TENS[tens] + (f" {ONES[ones]}" if ones else "")
    return str(n)


def workspace_to_text(name: str) -> str:
    """Turn a raw Hyprland workspace name into display text."""
    name = name.strip()
    if name.lstrip("-").isdigit():
        return number_to_words(int(name))
    # named / special workspace, e.g. "special:magic" -> "Magic"
    return (name.split(":")[-1] or name).capitalize()


class State:
    """Thread-safe shared state between the socket listener and the printer."""

    def __init__(self):
        self.lock = threading.Lock()
        self.override_text = None
        self.override_until = 0.0

    def trigger(self, text: str):
        with self.lock:
            self.override_text = text
            self.override_until = time.time() + REVERT_TIMEOUT

    def current(self):
        now = time.time()
        with self.lock:
            if self.override_text and now < self.override_until:
                return self.override_text, "workspace"
        return datetime.datetime.now().strftime("%H:%M"), "clock"


def hypr_socket_path() -> str:
    runtime = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if not sig:
        return ""
    return f"{runtime}/hypr/{sig}/.socket2.sock"


def listen_hyprland(state: State):
    """Connect to Hyprland's event socket and react to workspace changes.

    Reconnects automatically if Hyprland restarts or the socket is not
    yet available. This is event driven -- no hyprctl polling.
    """
    last_seen = None
    while True:
        path = hypr_socket_path()
        if not path or not os.path.exists(path):
            time.sleep(1)
            continue
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(path)
                buf = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        event = line.decode("utf-8", "ignore")
                        name = None
                        if event.startswith("workspacev2>>"):
                            payload = event.split(">>", 1)[1]
                            _, _, name = payload.partition(",")
                        elif event.startswith("workspace>>"):
                            name = event.split(">>", 1)[1]
                        if name and name != last_seen:
                            last_seen = name
                            state.trigger(workspace_to_text(name))
        except (OSError, ConnectionError):
            time.sleep(1)


def main():
    state = State()
    threading.Thread(target=listen_hyprland, args=(state,), daemon=True).start()

    last_output = None
    while True:
        text, css_class = state.current()
        output = {
            "text": text,
            "class": css_class,
            "tooltip": datetime.datetime.now().strftime("%A, %d %B %Y"),
        }
        if output != last_output:
            print(json.dumps(output), flush=True)
            last_output = output
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
