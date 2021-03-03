FROM python:3.7-slim-stretch

RUN groupadd --system bots && useradd --system -g bots bot_women_day

RUN apt-get update ; \
    apt-get install -y \
	    gcc \
		libc6-dev \
		libssl-dev \
		libpq-dev \
		python-dev

EXPOSE 80

RUN mkdir -p /opt/bot_women_day
ENV APP_DIR /opt/bot_women_day
WORKDIR $APP_DIR

COPY app $APP_DIR/app/
RUN pip3 install --upgrade pip && pip3 install -r app/requirements.txt

USER bot_women_day

CMD ["python", "-m", "app.main"]
