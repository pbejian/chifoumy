FROM python:3.12-slim

# Bibliothèques système nécessaires à OpenCV (utilisé par mediapipe)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY models/ models/
COPY images/ images/
COPY RPSLS.png .
COPY .streamlit/config.toml .streamlit/config.toml

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
