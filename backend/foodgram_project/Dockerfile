FROM python:3.9-slim

WORKDIR /app

RUN apt-get update
RUN apt-get -y install libpq-dev gcc

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app

CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "0.0.0.0:8000"]
