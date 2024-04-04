FROM python:3.9

WORKDIR /app/configuration

COPY . .

# Run the Python script
RUN python docker_compose_configuration.py

# CMD ["python", "docker_compose_configuration.py"]
CMD ["echo", "docker-compose configuration completed"]
