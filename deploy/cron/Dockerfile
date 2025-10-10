FROM python:3.10

ENV TZ=Africa/Johannesburg
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY deployment-engine deployment-engine/

WORKDIR /srv/deployment-engine
RUN pip install -r requirements.txt

COPY deploy/cron/crontab /etc/cron.d/deployment-cron
RUN chmod 0644 /etc/cron.d/deployment-cron

RUN mkfifo /tmp/stdout

RUN crontab /etc/cron.d/deployment-cron

CMD env >> /etc/environment && cron && tail -f /tmp/stdout