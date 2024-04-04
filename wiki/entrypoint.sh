#!/bin/bash

# Run the health check script and start the dependent service once it stops
./check_health.sh 

echo "Starting dependent service..." 
python wiki.py