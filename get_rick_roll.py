#!/usr/bin/env python3
"""
get_rick_roll.py

Safe helper to open the Rick Astley video in the default browser.
"""

import webbrowser

class RickRoll:
    def get_rick_roll(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        # webbrowser will attempt to open the default browser; it's safe and OS-independent.
        webbrowser.open(url)
