FROM python:3.9-slim

WORKDIR /app

RUN apt-get update
RUN apt-get -y install libpq-dev gcc

COPY foodgram-project-react/requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . /app

CMD ["gunicorn", "foodgram_project.wsgi:application", "--bind", "127.0.0.1:8000"]
