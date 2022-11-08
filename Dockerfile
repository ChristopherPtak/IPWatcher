
FROM python:latest

RUN pip install requests
COPY ipwatcher.py /app/ipwatcher.py

WORKDIR /app
CMD ["python", "/app/ipwatcher.py"]

