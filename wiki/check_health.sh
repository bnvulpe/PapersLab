#!/bin/bash

# Parse docker-compose.txt to get services listed under depends_on for wiki
DEPENDENT_SERVICES=$(awk '/^ *depends_on:/ { p = 1; next } p && /^ *-/{print $2; next} {p = 0}' docker-compose.txt)

# Poll Docker's API to check if all dependent services have stopped
while true; do
    all_exited=true
    for service in $DEPENDENT_SERVICES; do
        status=$(docker inspect -f '{{.State.Status}}' "$service" 2>/dev/null)
        if [ "$status" != "exited" ]; then
            echo "Waiting for $service to stop..."
            all_exited=false
            break
        fi
    done

    if $all_exited; then
        echo "All dependent services have stopped."
        break
    fi

    sleep 1
done

