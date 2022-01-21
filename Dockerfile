FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1
RUN apk update&& apk add postgresql-dev gcc python3-dev musl-dev

WORKDIR /company_details

COPY Pipfile .

COPY Pipfile.lock .

RUN pip3 install pipenv

RUN pipenv install

