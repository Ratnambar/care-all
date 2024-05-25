FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN mkdir /careall

WORKDIR /careall

ADD . /careall

RUN pip install -r requirements.txt