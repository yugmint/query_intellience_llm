FROM python:3.10-slim

WORKDIR /app

# System deps for faiss / torch / pypdf wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY main.py .

ENV LOG_LEVEL=INFO \
    FAISS_INDEX_PATH=/data/vectorstore

# GROQ_API_KEY must be supplied at runtime (docker run -e / compose env) --
# cred.json is not baked into the image since it's gitignored and holds a secret.

VOLUME ["/data"]

EXPOSE 8001

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]
