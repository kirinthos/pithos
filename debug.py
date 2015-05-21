#!/usr/bin/env python3

import os
import sys

# None of this works on Windows atm
if sys.platform != 'win32':
    # Enable verbose logging and test mode
    if len(sys.argv) == 1:
        sys.argv.append('-tvv')

from pithos import application

application.main()
