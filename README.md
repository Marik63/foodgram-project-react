# praktikum_new_diplom

![workflow](https://github.com/Marik63/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Демо рабочего проекта:
http://84.252.139.70/ или http://maratpraktik2.ddns.net

### реквизиты для входа под суперпользователем
```
admin user: marat63@mail.ru
password: 123456
```

## Описание проекта
# Foodgram - «Продуктовый помощник»

Приложение, на котором пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стек

- Python 3.7.0
- Django 2.2.19
- DRF 3.12.4
- Nginx
- Docker-compose
____

### Используемые технологии:

- Django 2.2.19
- Python 3.7.0
- Django REST Framework 3.12.4
- Simple-JWT 4.8.0
- PostgreSQL 13.0-alpine
- Nginx 1.21.3-alpine
- Gunicorn 20.0.4
- Docker 20.10.17, build 100c701
- Docker-compose 3.8


## Запуск проекта с помощью Docker

1. Склонируйте репозиторий на локальную машину.

    ```
    git clone git@github.com/Marik63/foodgram-project-react.git
    ```

2. Создайте .env файл в директории backend/foodgram/, в котором должны содержаться следующие переменные для подключения к базе PostgreSQL:

```
SECRET_KEY='your Django secret key'

DB_ENGINE=django.db.backends postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

DOCKER_PASSWORD=<Docker password>
DOCKER_USERNAME=<Docker username>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ(cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<id вашего телеграм-аккаунта(@userinfobot, команда /start)>
TELEGRAM_TOKEN=<токен вашего бота(@BotFather, /token, имя бота)>
```

3. Перейдите в директорию infra/ и выполните команду для создания и запуска контейнеров.
    ```
    sudo docker compose up -d --build
    ```
> Возможна команда **$ sudo docker-compose up -d --build** (зависит от версии docker compose)

> В Windows команда выполняется без **sudo**

4. В контейнере backend выполните миграции, создайте суперпользователя и соберите статику.

    ```
    sudo docker compose exec backend python manage.py migrate
    sudo docker compose exec backend python manage.py createsuperuser
    sudo docker compose exec backend python manage.py collectstatic --no-input 
    ```

5. Загрузите в БД ингредиенты командой ниже.

    ```
    sudo docker compose exec backend python manage.py load_ingredients
    ```

---
## **Разработчик проекта:**

- Марат Хайрутдинов: https://github.com/Marik63
