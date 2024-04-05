#!/bin/bash

> services_status.txt
# Run the status script to check the status of the services
# ./check_status.sh

DEPENDENT_SERVICES=()
in_depends_on=false
wiki_on=false

while IFS= read -r line; do
    # Check if the line contains the word "wiki:" using grep
    if grep -q "wiki:" <<< "$line"; then
        wiki_on=true
        echo "wiki is in this line: $line"
    fi

    # Check if the line contains "depends_on:" using grep
    if grep -q "depends_on:" <<< "$line"; then
        in_depends_on=true
        echo "depends_on is in this line: $line"
    fi

    # Check if both "wiki:" and "depends_on:" have been encountered before
    if $in_depends_on && $wiki_on; then
        # Check if the line contains "volumes:" using grep
        if grep -q "volumes:" <<< "$line"; then
            echo "Reached volumes section in this line: $line"
            break
        fi

        # Check conditions using grep and regex for extracting service names
        if grep -qE '^\s*-\s*([a-zA-Z0-9_]+):?' <<< "$line"; then
            service_name=$(grep -oP '^\s*-\s*\K([a-zA-Z0-9_]+)' <<< "$line")
            echo "Found dependent service: $service_name"  # Debug: Print found service
            DEPENDENT_SERVICES+=("$service_name")
        fi
    fi
done < docker-compose.txt

echo "Dependent Services: ${DEPENDENT_SERVICES[@]}"

function check_container_state() {
    local container_name="$1"
    local container_status=$(curl -sS "$DOCKER_API_URL/containers/$container_name/json" | jq -r '.State.Status')

    if [ "$container_status" = "running" ]; then
        echo "$container_name: running" >> services_status.txt
    else
        echo "$container_name: exited" >> services_status.txt
    fi
}

# Iterate over the services and check their status
while true; do
    all_exited=true
    for service in "${SERVICES[@]}"; do
        check_container_state "$service"

        if [ "$container_status" != "exited" ]; then
            echo "Waiting for $service to stop..."
            all_exited=false
        fi
    done

    if $all_exited; then
        echo "All dependent services have stopped."
        break
    fi

    sleep 1
done

# Poll Docker's API to check if all dependent services have stopped
# while true; do
#     all_exited=true
#     for service in "${DEPENDENT_SERVICES[@]}"; do
#         container_pid=$(ps -ef | grep "docker-containerd-shim.*$service" | grep -v grep | awk '{print $2}')

#         if [ -n "$container_pid" ]; then
#             state="running"
#             echo "$service: running" >> services_status.txt
#             echo "Waiting for $service to stop..."
#             all_exited=false
#         else
#             state="exited"
#             echo "$service: exited" >> services_status.txt
#         fi
        
        # Check if the container exists
        # if docker ps -a --format '{{.Names}}' | grep -q "^$service$"; then
            # Check the state of the container
        #     state=$(docker inspect -f '{{.State.Status}}' "$service")
        #     if [ "$state" != "exited" ]; then
        #         echo "Waiting for $service to stop..."
        #         all_exited=true
        #         break
        #     fi
        # fi
#     done

#     if $all_exited; then
#         echo "All dependent services have stopped."
#         break
#     fi

#     sleep 1
# done