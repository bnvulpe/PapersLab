#!/bin/bash

echo "Current directory:"
pwd  # Print working directory

echo "Documents in the directory:"
ls -l
# Run the health check script in the background
./check_health.sh &

# Start the main application
echo "Starting dependent service..."
python wiki.py