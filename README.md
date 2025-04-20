## Проект на автомат за экзамены по двум дисциплинам
### Александр Силицкий, ГБПОУ "Колледж связи №54" им. П.М. Вострухина, группа 1АСС11-8, отделение ОП-6 АСТ
Бот развёртывается посредством включения контейнера Docker на VPS-сервер и его установки через SSH. Для хранения секретов вместо .env-файла реализованы переменные среды в GitHub Actions. Небезопасное хранение токена в самом репозитории обусловлено самим пайплайном процесса развёртывания приложения, в ходе которого контейнеризованное приложение вытягивает токен из конфигурационного INI-файла. Также реализована возможность одновременного подъёма бота и базы через Docker Compose (`compose.yaml`). Бот асинхронный, написан на Python 3.13, в качестве БД используется PostgreSQL. Планируется реализация считывания запроса для автоинициализации БД из файла. Так как покрытие кода 80% достичь практически проблематично, отсутствие тестов компенсируется значительной работой, проделанной в сфере DevOps|CI/CD и настройки деплоймента.

# Telegram Bot Task Planner

This is a Telegram bot designed to help you manage your tasks efficiently. The bot provides the following functionalities:

- **List Tasks**: View all your current tasks.
- **Create Task**: Add a new task to your list.
- **Delete Task**: Remove a task from your list.
- **Edit Task**: Modify an existing task.

## Features

- Simple and intuitive task management via Telegram.
- Persistent storage using PostgreSQL.
- Easy deployment with Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your system.
- A Telegram bot token. You can obtain one by creating a bot through [BotFather](https://core.telegram.org/bots#botfather).

## Installation

1. Clone this repository:
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. Install the required packages.
    ```pip install -r requirements.txt```

3. Modify the `config.ini` file to meet your requirements
    ```[database]
    user = postgres
    password = Passlogin1.
    host = db
    dbname = project
    port = 5432
    ```

4. Edit the `compose.yaml` file to correspond the PostgreSQL settings to ones outlined in the bot configuration.

5. Start the application using Docker Compose:
    ```bash
    docker-compose up --build
    ```

6. The bot will now be running and connected to your Telegram account.

## Project Structure

- `./` - Contains the bot's source code.
- `./compose.yaml` - Configuration file for Docker Compose.
- `./config.ini` - Contains a configuration script for the bot.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.
