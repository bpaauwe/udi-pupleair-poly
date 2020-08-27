#!/usr/bin/env python3
"""
Polyglot v2 node server Purple Air data
Copyright (C) 2020 Robert Paauwe
"""

try:
    import polyinterface
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
from nodes import purpleair

LOGGER = polyinterface.LOGGER

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('purpleair')
        polyglot.start()
        control = purpleair.Controller(polyglot)
        control.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

