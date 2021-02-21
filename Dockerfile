FROM python:3.8-slim-buster

WORKDIR /code

COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential python3 python-dev python3-dev

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
