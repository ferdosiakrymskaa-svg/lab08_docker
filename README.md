## Лабораторная работа по работе с docker
Работа посвящена изучению технологии работы с контейнерами

## Задачи

- [ ] 1. Ознакомиться со ссылками учебного материала
- [ ] 2. Выполнить инструкцию учебного материала
- [ ] 3. Составить отчет и отправить ссылку преподавателю 

## Задание лабораторной работы

```bash
$ export GITHUB_USERNAME=<имя_пользователя>
$ export GIST_TOKEN=<сохраненный_токен>
$ alias edit=<nano|vi|vim|subl>
```

```sh
$ git clone https://github.com/${GITHUB_USERNAME}/lab06 projects/lab_docker
$ cd projects/lab_docker
$ git remote remove origin
$ git remote add origin https://github.com/${GITHUB_USERNAME}/lab_docker
```

```sh
# Debian
$ sudo apt-get update
$ sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```sh
$ cat >> main.py <<EOF
print("Hello, Docker!")
EOF
```

```sh
$ cat >> requirements.txt <<EOF
flask
requests
EOF
```

```sh
$ cat >> Dockerfile <<EOF
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential 

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
EOF
```

```sh
$ docker build -t lab-docker .
$ docker run --rm -it lab-docker
```

### Docker compose

```sh
$ cat >> docker-compose.yml <<EOF
version: '3.8'

services:
  app:
    build: . 
    container_name: lab_docker
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_HOST=$DB_HOST
      - DB_USER=$DB_USER
      - DB_PASSWORD=$DB_PASSWORD
      - DB_NAME=$DB_NAME

  # Сервис базы данных MySQL
  db:
    image: mysql:8.0
    container_name: mysql_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: $DB_ROOT_PASSWORD
      MYSQL_DATABASE: $DB_NAME
      MYSQL_USER: $DB_USER
      MYSQL_PASSWORD: $DB_PASSWORD
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db_data:
EOF
```

```sh
$ docker compose up --build
```

## Ссылки

### Docker compose

- [Install the Docker Compose plugin](https://docs.docker.com/compose/install/linux/)

### Dockerfile

- [Как запаковать простое приложение в Docker: на пальцах](https://habr.com/ru/companies/slurm/articles/930822/)

## Домашнее задание

В репозитории приведен код web-приложения, которое сохраняет в БД введенную информацию о задаче - ее имя.

## Часть I. Docker

1. Добавьте в код Dockerfile, который позволит запустить web-приложение с исходным кодом в каталоге app/ через docker.
2. Выполните запуск контейнера с этим приложением.
3. Скопируйте из консоли в каталог /home/ контейнера файл README.md.
4. Подключитесь к терминалу контейнера с приложением в интерактивном режиме. Проверьте, что скопированный файл находится в нужном каталоге.
5. Выйдите из интерактивного режима.
6. Остановите контейнер с приложением.


## Часть II. Docker compose
1. Создайте файл docker-compose.yml таким образом, чтобы совместно с описанным в части 1 контейнером работала бы база данных mysql. Файл инициализации БД в каталоге db/init.sql. Также пропишите порт подключения к приложению. Например 5000.
2. Запустите связку web-приложение - БД.
3. Проверьте подключение к приложению через браузер. Сделайте снимок экрана.
4. Проверьте работу приложения через браузер.

