#!/bin/bash

# Check if venv directory exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv based on OS
if [[ "$OSTYPE" == "msys" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Run setup.py
python pycycling/setup.py develop