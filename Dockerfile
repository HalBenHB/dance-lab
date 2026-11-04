# Dance Lab online. Needs DANCE_LAB_PASSWORD; see docs/online.md.
FROM python:3.13-slim-trixie

# Node solves YouTube's JavaScript challenges for yt-dlp; ffmpeg tidies the downloaded m4a files
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only what the online server serves
COPY server.py index.html ./
COPY wheres-the-one ./wheres-the-one

ENV PYTHONUNBUFFERED=1 DANCE_LAB_HOSTED=1
CMD ["python", "server.py"]
