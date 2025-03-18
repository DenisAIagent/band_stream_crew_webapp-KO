FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5003

CMD ["gunicorn", "--bind", "0.0.0.0:5003", "marketing_agents:app"]
