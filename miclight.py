#!/usr/bin/env python3

"""
adapted from https://github.com/Dzeri96/Micmute-LED-Pulseaudio-Service
"""

import os
import sys
import signal
import logging
import pulsectl

# config
# TODO: read from subprocess (`pactl get-default-source`)
mic_name = "alsa_input.pci-0000_04_00.6.HiFi__hw_acp__source"
led_mapping = "/sys/class/leds/platform::micmute/brightness"

# instantiate client
pulse = pulsectl.Pulse("miclight")

# global variable to track pulse events
pulse_event = None # : pulsectl.PulseEventInfo

def catch_events(e) -> None:
    global pulse_event
    logging.debug(f"Received Pulse event: {e}")
    pulse_event = e
    raise pulsectl.PulseLoopStop

def update_led(value: bool) -> None:
    print("on" if value else "off")
    with open(led_mapping, "w") as f:
        f.write("1" if value else "0")
    logging.debug("Wrote to mapping")

def start() -> int:
    logging.info("Starting...")
    pulse.connect(wait=True)
    logging.info("Connected!")

    active_index = -1
    logging.debug("Available sources:", pulse.source_list())
    for source in pulse.source_list():
        if source.name == mic_name:
            active_index = source.index

    if active_index == -1:
        raise RuntimeError(f"Unable to find mic: {mic_name}")

    led_value = not pulse.source_info(active_index).mute # type: ignore
    update_led(led_value)

    pulse.event_mask_set("all")
    pulse.event_callback_set(catch_events)

    return active_index

def stop(*_) -> None:
    logging.info("Stopping...")
    pulse.disconnect()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    active_index = start()

    while True:
        try:
            pulse.event_listen()
        except pulsectl.pulsectl.PulseDisconnected:
            # TODO: better reconnection
            logging.warning("Disconnected! Attempting to reconnect...")
            active_index = start()
        if pulse_event.index == active_index: # type: ignore 
            led_value = not pulse.source_info(active_index).mute # type: ignore
            update_led(led_value)
