from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class TaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_task_id_to_delete = State()
    waiting_for_task_id_to_edit = State()
    waiting_for_new_title = State()
    waiting_for_new_description = State()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать задачу")],
        [KeyboardButton(text="Удалить задачу")],
        [KeyboardButton(text="Редактировать задачу")],
        [KeyboardButton(text="Список задач")]
    ],
    resize_keyboard=True
)

def register_handlers(dp: Dispatcher, db_pool):

    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE telegram_id=$1", message.from_user.id)
            if not user:
                await conn.execute("""
                    INSERT INTO users (telegram_id, first_name, last_name, username)
                    VALUES ($1, $2, $3, $4)
                """, message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        await message.answer("Привет! Я бот для управления задачами.", reply_markup=main_kb)

    @dp.message(lambda m: m.text == "Создать задачу")
    async def create_task_prompt(message: types.Message, state: FSMContext):
        await message.answer("Введите название задачи:")
        await state.set_state(TaskStates.waiting_for_title)

    @dp.message(TaskStates.waiting_for_title)
    async def get_title(message: types.Message, state: FSMContext):
        await state.update_data(title=message.text)
        await state.set_state(TaskStates.waiting_for_description)
        await message.answer("Введите описание задачи:")

    @dp.message(TaskStates.waiting_for_description)
    async def get_description(message: types.Message, state: FSMContext):
        data = await state.get_data()
        title = data["title"]
        description = message.text
        await state.clear()

        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            await conn.execute("""
                INSERT INTO tasks (user_id, title, description)
                VALUES ($1, $2, $3)
            """, user_id, title, description)
        await message.answer("Задача создана ✅")

    @dp.message(lambda m: m.text == "Удалить задачу")
    async def delete_task_prompt(message: types.Message, state: FSMContext):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач для удаления.")
                return
            task_list = "\n".join([f"{t['id']}: {t['title']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи для удаления:")
            await state.set_state(TaskStates.waiting_for_task_id_to_delete)

    @dp.message(TaskStates.waiting_for_task_id_to_delete)
    async def delete_task(message: types.Message, state: FSMContext):
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Пожалуйста, введите корректный числовой ID задачи.")
            return

        async with db_pool.acquire() as conn:
            result = await conn.execute("DELETE FROM tasks WHERE id=$1", task_id)
            if result.endswith("DELETE 1"):
                await message.answer("Задача удалена ✅")
            else:
                await message.answer("Задача с таким ID не найдена ❌")
        await state.clear()

    @dp.message(lambda m: m.text == "Редактировать задачу")
    async def edit_task_prompt(message: types.Message, state: FSMContext):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач для редактирования.")
                return
            task_list = "\n".join([f"{t['id']}: {t['title']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n{task_list}\nВведите ID задачи для редактирования:")
            await state.set_state(TaskStates.waiting_for_task_id_to_edit)

    @dp.message(TaskStates.waiting_for_task_id_to_edit)
    async def ask_new_title(message: types.Message, state: FSMContext):
        try:
            task_id = int(message.text)
        except ValueError:
            await message.answer("Введите корректный ID задачи.")
            return

        await state.update_data(task_id=task_id)
        await message.answer("Введите новое название задачи:")
        await state.set_state(TaskStates.waiting_for_new_title)

    @dp.message(TaskStates.waiting_for_new_title)
    async def ask_new_description(message: types.Message, state: FSMContext):
        await state.update_data(new_title=message.text)
        await message.answer("Введите новое описание задачи:")
        await state.set_state(TaskStates.waiting_for_new_description)

    @dp.message(TaskStates.waiting_for_new_description)
    async def update_task(message: types.Message, state: FSMContext):
        data = await state.get_data()
        task_id = data["task_id"]
        new_title = data["new_title"]
        new_description = message.text

        async with db_pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE tasks SET title=$1, description=$2 WHERE id=$3",
                new_title, new_description, task_id
            )
            if result.endswith("UPDATE 1"):
                await message.answer("Задача обновлена ✅")
            else:
                await message.answer("Ошибка при обновлении задачи ❌")
        await state.clear()

    @dp.message(lambda m: m.text == "Список задач")
    async def list_tasks(message: types.Message):
        async with db_pool.acquire() as conn:
            user_id = await conn.fetchval("SELECT id FROM users WHERE telegram_id=$1", message.from_user.id)
            tasks = await conn.fetch("SELECT id, title, description FROM tasks WHERE user_id=$1", user_id)
            if not tasks:
                await message.answer("У вас нет задач.")
                return
            task_list = "\n\n".join([f"ID: {t['id']}\nНазвание: {t['title']}\nОписание: {t['description']}" for t in tasks])
            await message.answer(f"Ваши задачи:\n\n{task_list}")
