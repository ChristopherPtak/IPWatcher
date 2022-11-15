
FROM python:latest

RUN pip install requests
COPY app.py /app/app.py

WORKDIR /app
CMD ["python", "/app/app.py"]

