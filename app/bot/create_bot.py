from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers.admin_router import admin_router
from app.bot.handlers.user_router import user_router

from app.config import settings

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()



async def notify_admins(message):
    try:
        await bot.send_message(settings.ADMIN_ID, message)
    except Exception as e:
        logger.error(
            f"Ошибка при отправке сообщения администратору {settings.ADMIN_ID}: {e}"
        )


async def start_bot():

    dp.include_router(user_router)
    dp.include_router(admin_router)

    await notify_admins("Я запущен🥳.")
    logger.info("Бот успешно запущен.")


async def stop_bot():
    await notify_admins("Бот остановлен. За что?😔")
    logger.error("Бот остановлен!")
