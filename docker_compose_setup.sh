#!/bin/bash

# Function to log messages with a timestamp and header
log_message() {
    echo -e "\n$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a logs/docker_compose.log
}

# Ensure the script exits on the first error
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Overwrite the log files if they exist
> logs/docker_compose.log
> logs/docker.logs

# Start logging
log_message "### Docker Compose Setup Started ###"

# Docker Compose down
log_message "### Docker Compose Down ###"
docker compose down | tee -a logs/docker_compose.log

# Cleanup Docker resources
log_message "### Docker Resource Cleanup Prompt ###"
read -p "This will remove all volumes, images, and everything connected to the current containers. Are you sure? (y/N) " REPLY
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_message "### Docker Resource Cleanup ###"
    docker compose down --volumes --rmi all --remove-orphans | tee -a logs/docker_compose.log
    docker system prune -af --volumes | tee -a logs/docker_compose.log
    log_message "Cleanup completed."
else
    log_message "Cleanup cancelled."
fi

# Docker Compose build
log_message "### Docker Build Logs ###"
docker compose build --progress=plain 2>&1 | tee -a logs/docker_compose.log

# Run Docker Compose up and down 3 times for testing with timeout
for i in {1..3}; do
    log_message "### Docker Run #$i Container Startup ###"
    log_message "Waiting for 30 seconds before stopping containers..."
    docker compose up --build --timeout 30 --dry-run 2>&1 | tee -a logs/docker_compose.log


    log_message "### Docker Run #$i Container Shutdown ###"
    docker compose down | tee -a logs/docker_compose.log
done


# Gather information on the build and containers
log_message "### Docker Image Information ###"
docker compose images 2>&1 | tee -a logs/docker_compose.log

log_message "### Docker Container Status ###"
docker compose ps 2>&1 | tee -a logs/docker_compose.log

# Extract errors from the log
log_message "### Extracting Errors from Logs ###"
grep -i "error" logs/docker_compose.log > logs/docker_errors.log || log_message "No errors found."

# Provide final status
log_message "### Docker Setup and Testing Completed ###"
log_message "Logs can be found in logs/docker_compose.log."
log_message "Any errors encountered during the process are logged in logs/docker_errors.log."

# Display the errors log if any errors were found
if [ -s logs/docker_errors.log ]; then
    log_message "Errors were found during the Docker setup:"
    cat logs/docker_errors.log | tee -a logs/docker_compose.log
else
    log_message "No errors were found during the Docker setup."
fi


# Ask user if containers should stay active or be stopped
read -p "Do you want to keep the containers active? (Y/n): " KEEP_ACTIVE

if [[ $KEEP_ACTIVE =~ ^[Nn]$ ]]; then
    log_message "### Stopping Docker Containers ###"
    docker compose stop 2>&1 | tee -a logs/docker_compose.log
    log_message "Docker containers have been stopped."
else
    log_message "### Active Docker Containers ###"
    docker compose up --build -d 2>&1 | tee -a logs/docker_compose.log
    log_message "Docker containers are now running in the background."
fi
