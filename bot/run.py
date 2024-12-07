import logging
import asyncio

from aiogram import Dispatcher
from handlers import router, bot

dp = Dispatcher()

async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')