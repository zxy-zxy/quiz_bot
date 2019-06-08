FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /quiz_bot/requirements.txt
RUN pip install -r /quiz_bot/requirements.txt

COPY ./src/ /quiz_bot/src/
COPY ./entrypoint.sh /quiz_bot/entrypoint.sh

RUN	chmod +x	/quiz_bot/entrypoint.sh

WORKDIR /quiz_bot/
