
FROM python:3.14-slim

# Установка завсисимостей для psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev

# Установка завсисимостей из requirements.txt
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# Копирование приложения
COPY . /app
WORKDIR app

ENTRYPOINT ["gunicorn", "server:app", "--bind", "0.0.0.0:5000"]
