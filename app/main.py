import asyncio
from loguru import logger
from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request

from aiogram.types import Update
from aiogram.exceptions import TelegramRetryAfter

from app.bot.create_bot import bot, dp, stop_bot, start_bot

from app.config import settings
from app.pages.router import router as router_pages
from app.api.router import router as router_api


@asynccontextmanager
async def lifespan(app: FastAPI):

    await start_bot()
    webhook_url = settings.get_webhook_url()
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != webhook_url:
            await bot.set_webhook(
                url=webhook_url,
                allowed_updates=dp.resolve_used_update_types(),
                drop_pending_updates=True,
            )
            logger.success(f"Вебхук установлен: {webhook_url}")
        else:
            logger.info("Вебхук уже установлен, повторная установка не требуется.")
    except TelegramRetryAfter as e:
        logger.warning(
            f"Ошибка установки вебхука: {e}. Повторная попытка через {e.retry_after} секунд."
        )
        await asyncio.sleep(e.retry_after)
    except Exception as e:
        logger.error(f"Ошибка при установке вебхука: {e}")

    yield
    await stop_bot()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), "static")


@app.post("/barber")
async def webhook(request: Request) -> None:
    logger.info("Received webhook request")
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    logger.info("Update processed")


app.include_router(router_pages)
app.include_router(router_api)
