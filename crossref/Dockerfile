FROM python:3.9

WORKDIR /app

COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt

# Add wait-for-it
COPY wait-for-it.sh wait-for-it.sh 
RUN chmod +x wait-for-it.sh

CMD ["python", "crossref.py"]
