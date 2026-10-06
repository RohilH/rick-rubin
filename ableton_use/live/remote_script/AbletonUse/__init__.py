# ableton-use bridge — an Ableton Live MIDI Remote Script.
#
# Install: copy this "AbletonUse" folder to your User Library "Remote Scripts"
# folder (or run `ableton-use install-bridge`), restart Live, then pick
# "AbletonUse" as a Control Surface in Settings > Link, Tempo & MIDI.
#
# Exposes a small newline-delimited JSON protocol on 127.0.0.1:9889. Requests
# are received on a background thread but every Live API call runs on Live's
# main thread (drained from a queue in update_display), which is required for
# thread safety.
from .bridge import AbletonUse


def create_instance(c_instance):
    return AbletonUse(c_instance)
