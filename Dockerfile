FROM python:3.9.12-slim-bullseye

RUN groupadd --system bots && useradd --system -g bots bot_women_day

RUN apt-get update ; \
    apt-get install -y \
	    gcc \
		libc6-dev \
		libssl-dev \
		libpq-dev \
		python-dev

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

EXPOSE 80

RUN mkdir -p /opt/bot_women_day
ENV APP_DIR /opt/bot_women_day
WORKDIR $APP_DIR

COPY src $APP_DIR/src/
RUN pip3 install --upgrade pip && pip3 install -r src/requirements.txt

USER bot_women_day

CMD ["python3", "-m", "src.main"]
