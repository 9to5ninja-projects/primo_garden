#!/bin/bash
# Quick run script - activates venv and runs simulation

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run ./setup.sh first."
    exit 1
fi

source venv/bin/activate
python main.py
