FROM python:3.8-slim-buster

COPY ./ /etc/reverse-bot-adventure

RUN pip install requests

VOLUME ["/etc/reverse-bot-adventure/logs", "/etc/reverse-bot-adventure/Settings"]

WORKDIR /etc/reverse-bot-adventure
CMD ["sh", "-c", "python -m Bot.Main"]