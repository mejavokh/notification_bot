import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from datetime import datetime, timedelta

API_TOKEN = '#'  # вставьте свой токен


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

reminders = {}


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я бот для напоминаний. Напиши мне что-то вроде 'напомни через 10 минут выпить воду'.")


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("Вы можете установить напоминание, написав что-то вроде "
                         "'напомни через 10 минут сделать что-то'.")


@dp.message_handler(lambda message: 'напомни' in message.text.lower())
async def set_reminder(message: types.Message):
    try:
        parts = message.text.lower().split(' ')
        time_index = parts.index('через') + 1
        time_value = int(parts[time_index])
        time_unit = parts[time_index + 1]

        if 'минут' in time_unit:
            delta = timedelta(minutes=time_value)
        elif 'час' in time_unit:
            delta = timedelta(hours=time_value)
        elif 'день' in time_unit:
            delta = timedelta(days=time_value)
        else:
            await message.reply("Не могу понять время. Попробуйте указать время в минутах, часах или днях.")
            return

        reminder_time = datetime.now() + delta
        reminder_text = ' '.join(parts[time_index + 2:])
        reminders[reminder_time] = (message.chat.id, reminder_text)

        await message.reply(f"Напоминание установлено через {time_value} {time_unit}: {reminder_text}")
    except Exception as e:
        await message.reply("Не удалось установить напоминание. Пожалуйста, проверьте формат сообщения.")


async def reminder_scheduler():
    while True:
        now = datetime.now()
        for reminder_time in list(reminders.keys()):
            if reminder_time <= now:
                chat_id, text = reminders.pop(reminder_time)
                await bot.send_message(chat_id, f"Напоминание: {text}")
        await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(reminder_scheduler())
    executor.start_polling(dp, skip_updates=True, loop=loop)

