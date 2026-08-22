#!/bin/bash
# Watchdog & Keep-Alive Script for Autonomous Translation Engine

PID=$(pgrep -f "autonomous_engine.py")

if [ -z "$PID" ]; then
    echo "[Watchdog] Engine not running. Starting autonomous_engine.py in background..."
    nohup python3 /Users/ricksabchez/workspace/autonomous_engine.py >> /Users/ricksabchez/workspace/engine_daemon.log 2>&1 &
    echo "[Watchdog] Started with PID: $!"
else
    echo "[Watchdog] Engine is healthy and running (PID: $PID)."
fi
