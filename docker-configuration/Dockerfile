FROM python:3.9

WORKDIR /app/configuration

COPY . .

# Run the Python script and redirect output to a log file
RUN python docker_compose_configuration.py > output.log

# If you want to see the contents of the log file, you can add a CMD or ENTRYPOINT command to display it
CMD ["cat", "output.log"]

# CMD ["python", "docker_compose_configuration.py"]
#CMD ["echo", "docker-compose configuration completed"]
