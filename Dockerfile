FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY OVH_CLI.py .

ENTRYPOINT ["python", "OVH_CLI.py"]
