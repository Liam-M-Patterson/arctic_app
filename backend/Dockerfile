FROM python:3.7-alpine
# FROM python:latest

WORKDIR /app

ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]