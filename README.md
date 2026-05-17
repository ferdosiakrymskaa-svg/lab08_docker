## Лабораторная работа по работе с docker
---
## Домашнее задание

Для начала рассмотрим все файлы, которые содержатся в данном проекте:
### `main.py`
```sh
print("Hello, Docker!")
```
Простая функция печати в `Python`, печатает `Hello, Docker!`

---
### `docker-compose.yml`
```sh
services:                     #Главный раздел в котором перечисляются контейнеры
  app:                        #Имя сервиса
    build: .                  #Указывает на то, что образ для этого сервиса нужно собрать из докера, который лежит в данной директории
    container_name: lab_docker#Задает имя контейнера
    ports:
      - "5000:5000"           # внешний:внутренний порт для сервиса app
    depends_on:               # управляет порядком запуска и условиями готовности. Контейнер app не стартует, пока не выполнится условие, заданное для сервиса db.    
      db: #имя сервиса, от которого зависит app.
        condition: service_healthy # ждать не просто старта контейнера db, а пока его healthcheck не сообщит статус healthy
    environment :# Задает переменные окружения, которые берутся из файла .env, который лежит в .gitignore в целях безопастности, обсуждаемых на семинаре
      - DB_HOST=${DB_HOST} #Переменные окржунения
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_NAME=${DB_NAME}

  db: # имя сервиса базы данных
    image: mysql:8.0 #использовать готовый образ MySQL версии 8.0 с Docker Hub
    container_name: mysql_db #Имя контейнера
    restart: always #если контейнер упадет, то произойдет рестарт
    environment: #Среда в которой будут определены переменные проиллюстрированные ниже
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    ports:
      - "3306:3306" #Проброс порта для сервиса db
    volumes: #подключение томов
      - db_data:/var/lib/mysql #именованный том db_data (объявлен ниже) монтируется в папку, где MySQL хранит свои данные. Это гарантирует, что данные сохранятся при пересоздании контейнера.
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql   # инициализация БД
    healthcheck: # проверка работоспособности контейнера
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"] #test: – команда, которая выполняется для проверки. Здесь mysqladmin ping -h localhost – стандартный способ узнать, отвечает ли MySQL.
      interval: 10s #запускать каждые 10 секунд
      timeout: 5s #время ожидания
      retries: 5 #количество повторов

volumes:#просто объявление тома с именем db_data
  db_data:
```
---
### `Dockerfile`
```sh
FROM python:3.9-slim #Указывает базовый образ на основе которого будет строиться контейнер

WORKDIR /app  #задает рабочую папку внутри контейнера

RUN apt-get update && apt-get install -y build-essential  # выполнение команды в процессе сборки образа

COPY app/requirements.txt . # копирует файл app/requirements.txt внутрь образа

RUN pip install --no-cache-dir -r requirements.txt #Устанавливает Python-зависимости, перечисленные в скопированном requirements.txt.
Флаг --no-cache-dir отключает кэширование pip, чтобы уменьшить размер образа 

COPY app/ . # Копирует все содержимое папки app

CMD ["python", "app.py"] # задает команду которая будет выполнена при запуске контенера
```
---

### `db/init.sql`
```sh
SET NAMES utf8mb4;

CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO items (name) VALUES ('Пример 1'), ('Пример 2');
```
Данный файл создаёт таблицу items с полями id и name, принудительно задав кодировку utf8mb4 для хранения данных. Исходный код был изменен, потому что не распозновался русский язык и выводились кракозябры:

<details> <summary>Вывод прошлой версии программы </summary>

Список из Базы Данных <br>
ÐŸÑ€Ð¸Ð¼ÐµÑ€ 1  <br>
ÐŸÑ€Ð¸Ð¼ÐµÑ€ 2  <br>

</details>

---

### `app/app.py`
```sh
from flask import Flask, render_template
from models import ItemModel

app = Flask(__name__)
model = ItemModel()

@app.route('/')
def index():
    # Контроллер запрашивает данные у модели
    items = model.get_all_items()
    # И передает их в представление (шаблон)
    return render_template('index.html', items=items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

---

### `app/models.py`
```sh
import os
import mysql.connector

class ItemModel:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'db'),
            'port': 3306,
            'user': os.getenv('DB_USER', 'user'),
            'password': os.getenv('DB_PASSWORD', 'userpass'),
            'database': os.getenv('DB_NAME', 'mydb'),
            'charset': 'utf8mb4',          # вот что реши проблему
            'collation': 'utf8mb4_unicode_ci'
        }

    def get_all_items(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT name FROM items')
            items = cursor.fetchall()
            cursor.close()
            conn.close()
            return items
        except Exception as e:
            print(f"Error: {e}")
            return []
```
Настройки подключения к MySQL: адрес, порт, учётные данные берутся из переменных окружения (с резервными значениями на случай, если переменные не заданы). Главное – явно указана кодировка utf8mb4, чтобы русский текст не искажался.
Метод def get_all_items(self) получает все записи из таблицы items. Если подключиться или выполнить запрос не удаётся, ошибка пишется в лог, но возвращается пустой список – приложение не падает.

---
## Часть I. Docker
Приступим непосредственно у выполнению домашней работы:
Первоначально Docker отсутствовал в системе. Была выполнена установка согласно официальной инструкции для Ubuntu 24.04:
```sh
# Добавление официального репозитория Docker
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
Для запуска Docker без прав суперпользователя текущий пользователь был добавлен в группу `docker` и выполнена перезагрузка сеанса (`newgrp docker`). Проверка – `docker run hello-world` – прошла успешно.
<details><summary>Вывод команды</summary>
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/

</details>

---

#### 1. Добавьте в код `Dockerfile`, который позволит запустить web-приложение с исходным кодом в каталоге app/ через docker.
Добавили код в файл, показали содержимое нового файла

---
#### 2. Выполните запуск контейнера с этим приложением.
Выполнить запуск контейнера можно командой `docker build -t lab-web .` (повторная сборка для иллюстрации работы):
<details>
    <summary>Вывод </summary>
     docker build -t lab-web .
[+] Building 2.7s (11/11) FINISHED                                                                                                                                       docker:default
 => [internal] load build definition from Dockerfile                                                                                                                               0.0s
 => => transferring dockerfile: 253B                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.9-slim                                                                                                                 1.5s
 => [internal] load .dockerignore                                                                                                                                                  0.0s
 => => transferring context: 2B                                                                                                                                                    0.0s
 => [internal] load build context                                                                                                                                                  0.0s
 => => transferring context: 204B                                                                                                                                                  0.0s
 => [1/6] FROM docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b                                                           0.1s
 => => resolve docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b                                                           0.1s
 => CACHED [2/6] WORKDIR /app                                                                                                                                                      0.0s
 => CACHED [3/6] RUN apt-get update && apt-get install -y build-essential                                                                                                          0.0s
 => CACHED [4/6] COPY app/requirements.txt .                                                                                                                                       0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                0.0s
 => CACHED [6/6] COPY app/ .                                                                                                                                                       0.0s
 => exporting to image                                                                                                                                                             0.5s
 => => exporting layers                                                                                                                                                            0.0s
 => => exporting manifest sha256:b6d1751709c54ae8cb43e4e64a1b33185d629fbeb831179b550521085b2f1317                                                                                  0.1s
 => => exporting config sha256:40271165584e95b776c25a3975bd63b5100fa30a6da44f6abec84591a8faeb4d                                                                                    0.0s
 => => exporting attestation manifest sha256:caf2192ec8cc5bf0b75953a2f7f260520b0c9c65976c2c62424e2600495f736a                                                                      0.1s
 => => exporting manifest list sha256:1f7b79f709becbaf06d601b25a15428c83c86190256ffdb62da4ad339e4852e0                                                                             0.1s
 => => naming to docker.io/library/lab-web:latest                                                                                                                                  0.0s
 => => unpacking to docker.io/library/lab-web:latest                                             
</details>

`docker run -d --name lab_container -p 5000:5000 lab-web`:
```txt
7217a952853c3c90815c14993c548a6241395efb2edae3d05579467237cb6827
```
Пояснение флагов:

- -d – detached mode, контейнер работает в фоне и не блокирует терминал.
-  --name lab_container – присваивает контейнеру фиксированное имя для удобства последующих команд.
- -p 5000:5000 – пробрасывает порт 5000 хоста на порт 5000 внутри контейнера, что позволяет обратиться к Flask из браузера.


---

#### 3. Скопируйте из консоли в каталог `/home/` контейнера файл `README.md`.
Скопировали командой `docker cp README.md lab_container:/home/`:
```txt
Successfully copied 4.44kB (transferred 6.14kB) to lab_container:/home/
```
---

#### 4. Подключитесь к терминалу контейнера с приложением в интерактивном режиме. Проверьте, что скопированный файл находится в нужном каталоге.
Команда `docker exec -it lab_container /bin/bash`
- exec – выполняет команду внутри уже запущенного контейнера.
- -it – интерактивный режим с TTY (позволяет взаимодействовать с оболочкой).
```txt
 ls /home/
README.md
```
---

#### 5. Выйдите из интерактивного режима.
Команда `exit`

---
#### 6. Остановите контейнер с приложением.
Останавливаем командой `docker stop lab_container`. Смотрим, что действительно остановилось командой ` docker ps -a`, где -a показывает даже остановленные
```txt
CONTAINER ID   IMAGE     COMMAND           CREATED         STATUS                        PORTS     NAMES
18cbb89d9b18   lab-web   "python app.py"   2 minutes ago   Exited (137) 14 seconds ago             lab_container
```
---
## Часть II. Docker compose
#### 1. Создайте файл `docker-compose.yml` таким образом, чтобы совместно с описанным в части 1 контейнером работала бы база данных `mysql`. Файл инициализации БД в каталоге d`b/init.sql`. Также пропишите порт подключения к приложению. Например 5000.
Создали `docker-compose.yml` и предоставили его раньше

---
#### 2. Запустите связку web-приложение - БД.
Команды:
```sh
docker compose down -v          # удаление старых контейнеров и томов
docker compose up -d --build    # сборка и запуск в фоне
```
- down -v – останавливает контейнеры и удаляет связанные тома (volumes), гарантируя чистую инициализацию.
- up -d – запускает сервисы в фоновом режиме.
- --build – принудительно пересобирает образ приложения перед запуском.

После старта контейнер mysql_db переходит в состояние healthy, и приложение становится доступно по адресу http://localhost:5000. Страница отобразила заголовок «Список из Базы Данных» и два элемента: «Пример 1», «Пример 2».

<details> <summary>Вывод команд </summary>
    
[+] down 2/2
 ✔ Network lab_docker_default Removed                                                                                                                                               0.2s
 ✔ Volume lab_docker_db_data  Removed                                                                                                                                               0.0s
[+] Building 2.2s (13/13) FINISHED                                                                                                                                                      
 => [internal] load local bake definitions                                                                                                                                         0.0s
 => => reading from stdin 584B                                                                                                                                                     0.0s
 => [internal] load build definition from Dockerfile                                                                                                                               0.0s
 => => transferring dockerfile: 253B                                                                                                                                               0.0s
 => [internal] load metadata for docker.io/library/python:3.9-slim                                                                                                                 0.7s
 => [internal] load .dockerignore                                                                                                                                                  0.1s
 => => transferring context: 2B                                                                                                                                                    0.0s
 => [1/6] FROM docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b                                                           0.2s
 => => resolve docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b                                                           0.1s
 => [internal] load build context                                                                                                                                                  0.1s
 => => transferring context: 204B                                                                                                                                                  0.0s
 => CACHED [2/6] WORKDIR /app                                                                                                                                                      0.0s
 => CACHED [3/6] RUN apt-get update && apt-get install -y build-essential                                                                                                          0.0s
 => CACHED [4/6] COPY app/requirements.txt .                                                                                                                                       0.0s
 => CACHED [5/6] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                0.0s
 => CACHED [6/6] COPY app/ .                                                                                                                                                       0.0s
 => exporting to image                                                                                                                                                             0.5s
 => => exporting layers                                                                                                                                                            0.0s
 => => exporting manifest sha256:9a5a9fa6bbfb48e85a514f80a25bbe577f66657a0ade133cac29914f7c7ac492                                                                                  0.0s
 => => exporting config sha256:7a46bddfbcc40f66d119f0f05a50e64abdbf07e88f6bd22a1ae2f3139e574efe                                                                                    0.0s
 => => exporting attestation manifest sha256:34ffe89cae93235a44d1121851c9d78f9c53f0ae688c8f1c46ca918b65df216c                                                                      0.1s
 => => exporting manifest list sha256:2c091953277d9d77fcc4e9cb0a81d12d91a5990d65193d52b4619f15ee823dcb                                                                             0.1s
 => => naming to docker.io/library/lab_docker-app:latest                                                                                                                           0.0s
 => => unpacking to docker.io/library/lab_docker-app:latest                                                                                                                        0.0s
 => resolving provenance for metadata file                                                                                                                                         0.0s
[+] up 5/5
 ✔ Image lab_docker-app       Built                                                                                                                                                 3.3s
 ✔ Network lab_docker_default Created                                                                                                                                               0.1s
 ✔ Volume lab_docker_db_data  Created                                                                                                                                               0.0s
 ✔ Container mysql_db         Healthy                                                                                                                                              21.6s
 ✔ Container lab_docker       Started          
    
</details>

#### 3. Проверьте подключение к приложению через браузер. Сделайте снимок экрана.
#### 4. Проверьте работу приложения через браузер.
Шаги 3 и 4 выполнили одновременно


<img width="699" height="495" alt="Screenshot from 2026-05-17 22-01-11" src="https://github.com/user-attachments/assets/b73820f9-bf73-4613-acda-2a2e51838127" />
