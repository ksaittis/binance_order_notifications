FROM python:3.8-alpine3.11

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]
