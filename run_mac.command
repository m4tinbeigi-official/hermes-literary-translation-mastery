#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Hermes Book Translator..."
python3 app.py || python app.py
