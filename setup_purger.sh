#!/bin/bash

# Dynamically detect script directory
BOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "🚀 Starting bot configuration in $BOT_DIR..."
cd "$BOT_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
echo "Installing dependencies..."
./venv/bin/pip install -r requirements_purger.txt

echo "✅ Configuration finished!"
echo "You can now run the bot using:"
echo "cd '$BOT_DIR' && ./venv/bin/python purger_bot.py"
