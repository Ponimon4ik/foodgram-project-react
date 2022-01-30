#Foodgram, кулинарный сайт с проверенными на собственной кухне рецептами

### Используемые технологии:

+ Django,
+ Django rest framework
+ Python
+ Docker

### Установка Docker:

Установите Docker
```
sudo apt install docker
```

Установите docker-compose, с этим вам поможет [официальная документация](https://docs.docker.com/compose/install/)

### Как запустить проект:

Клонировать репозиторий и перейти в директорию infra:
```
git clone https://github.com/Ponimon4ik/foodgram-project-react
```
```
cd infra
```

Cоздать env-файл и прописать переменные окружения в нём:
```
touch .env
```
```
DEBUG_STATUS = FALSE # устанавливаем режим отладки
ALLOWED_HOST = ['*'] # указываем разрешенные хосты (установите свои)
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY= secret_key_django # ключ django приложения
```

Запустить docker-compose
```
docker-compose up -d
```

Выполнить по очереди команды:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

### Как загрузить ингредиенты:

Выполнить команду:
```
docker-compose exec web python manage.py loaddata fixtures.json
```

### Автор:

+ Стефанюк Богдан

### Ссылка на проект:
[Foodgram_project](http://51.250.4.172:80/)
![Foodgram_project_workflow](https://github.com/Ponimon4ik/foodgram-project-react/workflows/foodgram_project/badge.svg)