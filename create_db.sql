-- Таблица пользователей Telegram
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE, -- chat_id или user_id из Telegram
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    is_bot_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица задач
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' -- варианты: pending, in_progress, completed
);

-- Триггер для автоматического обновления поля updated_at при изменении записи в tasks
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();

-- Таблица учёта времени, потраченного на задачу
CREATE TABLE time_entries (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    duration INTERVAL NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL
);

-- Таблица комментариев к задачам
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Удаление зависимых таблиц
-- DROP TABLE IF EXISTS comments;
-- DROP TABLE IF EXISTS time_entries;
-- DROP TABLE IF EXISTS tasks;

-- Удаление основной таблицы пользователей
-- DROP TABLE IF EXISTS users;

-- Удаление триггера и функции
-- DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
-- DROP FUNCTION IF EXISTS update_updated_at_column;
