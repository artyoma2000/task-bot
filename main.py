import asyncio
import logging

import asyncpg
from aiogram import Bot, Dispatcher
from config import load_config
from db import create_pool
from handlers import register_handlers

config = load_config()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot.token)

dp = Dispatcher()

DB_CONFIG = {
    "user": config.db.user,
    "password": config.db.password,
    "database": config.db.dbname,
    "host": config.db.host,
    "port": 5432
}
DROP_TABLES = False


TABLE_CHECK_SQL = """
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public' AND table_name IN ('users', 'tasks', 'time_entries', 'comments');
"""

CREATE_SQL = """
-- Таблица пользователей Telegram
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    is_bot_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица задач
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);

-- Функция и триггер
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Таблица учета времени
CREATE TABLE IF NOT EXISTS time_entries (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    duration INTERVAL NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL
);

-- Таблица комментариев
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DROP_SQL = """
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS time_entries;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;
DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
DROP FUNCTION IF EXISTS update_updated_at_column;
"""

async def main():
    db_pool = await create_pool(config)
    register_handlers(dp, db_pool)
    await dp.start_polling(bot)

async def init_db():
    conn = await asyncpg.connect(**DB_CONFIG)
    print("✅ Подключение к БД успешно.")

    if DROP_TABLES:
        print("⚠️ Удаление существующих таблиц...")
        await conn.execute(DROP_SQL)

    result = await conn.fetch(TABLE_CHECK_SQL)
    existing_tables = {row["table_name"] for row in result}

    expected_tables = {'users', 'tasks', 'time_entries', 'comments'}
    if expected_tables.issubset(existing_tables):
        print("✅ Все таблицы уже существуют.")
    else:
        print("📦 Создание недостающих таблиц...")
        await conn.execute(CREATE_SQL)
        print("✅ Таблицы успешно созданы.")

    await conn.close()
if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(main())