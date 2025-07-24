FROM python:3.12.11-slim-bullseye

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN groupadd -r nonroot && useradd -r -g nonroot nonroot

USER nonroot

WORKDIR /app

COPY . .

CMD ["python", "main.py"]