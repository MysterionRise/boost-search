FROM python:3.8.5-buster

RUN mkdir /opt/qa-api && useradd --create-home qa && \
    chown qa -R /opt/qa-api

WORKDIR /opt/qa-api

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY main.py ./
COPY app/ ./app
COPY swagger ./swagger

USER qa

EXPOSE 8080
CMD ["gunicorn", "--workers=2", "--bind=:8080", "main:create_app()"]
