FROM python:3.9.5-slim-buster

RUN mkdir /app
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt

COPY main.py /app/main.py
COPY utils.py /app/utils.py

WORKDIR /app
CMD ["streamlit", "run", "main.py"]