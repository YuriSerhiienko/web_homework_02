FROM python:3.10-alpine

COPY . ./bot
WORKDIR /bot
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "src/pymakers/bot.py" ]