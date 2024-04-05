FROM python:3.9

WORKDIR /app

COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x entrypoint.sh
# Deletes \r from Windows files
RUN sed -i 's/\r$//' entrypoint.sh 
RUN sed -i 's/\r$//' check_health.sh 

ENTRYPOINT ["./entrypoint.sh"]
