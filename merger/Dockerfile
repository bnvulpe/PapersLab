FROM python:3.9

WORKDIR /app

# Download wait-for-it.sh script
RUN curl -o wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh

# Make the script executable
RUN chmod +x wait-for-it.sh

# Copy the rest of the application files
COPY ./ ./

CMD ["python", "merge.py"]
