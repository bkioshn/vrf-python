FROM python:3.8-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt update
RUN apt install build-essential -y
RUN apt install libpq-dev -y
RUN pip3 install Flask gunicorn
RUN pip3 install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 evm-listener:app