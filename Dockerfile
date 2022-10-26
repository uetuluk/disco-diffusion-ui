FROM python:3.10-slim as base

EXPOSE 8501

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

FROM base as app

ENV SERVER_LOCATION='localhost:5000'

COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "gui.py", "--server.port=8501", "--server.address=0.0.0.0"]