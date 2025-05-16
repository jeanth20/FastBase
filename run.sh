#!/bin/bash
echo "Running FastBase..."

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment and run the application
source venv/bin/activate
python run.py
