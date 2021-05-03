FROM python:3.8-slim-buster

RUN pip install requests isodate scipy

COPY ./ /etc/reverse-bot-adventure

VOLUME ["/etc/reverse-bot-adventure/logs", "/etc/reverse-bot-adventure/Settings"]

WORKDIR /etc/reverse-bot-adventure
CMD ["sh", "-c", "python -m Bot.Main"]