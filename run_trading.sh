#!/bin/bash

# Load environment variables
if [ -f "$(dirname "$0")/.env" ]; then
    source "$(dirname "$0")/.env"
else
    echo ".env file not found"
    exit 1
fi

# Change to the trading directory
cd ~/trading || { echo "Directory ~/trading not found"; exit 1; }

# Activate the virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found in ~/trading/venv"
    exit 1
fi

# Run the portfolio analysis script
python3 run_and_save.py
