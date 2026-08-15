from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from db import Database


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, db: Database):
        self.db = db
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["db"] = self.db

        if isinstance(event, Message) and event.from_user:
            await self.db.add_user(
                telegram_id=event.from_user.id,
                username=event.from_user.username,
                full_name=event.from_user.full_name
            )
            if event.text:
                await self.db.log_message(event.from_user.id, event.text)

        elif isinstance(event, CallbackQuery) and event.from_user:
            await self.db.add_user(
                telegram_id=event.from_user.id,
                username=event.from_user.username,
                full_name=event.from_user.full_name
            )

        return await handler(event, data)
