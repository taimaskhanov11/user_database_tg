from typing import Callable, Dict, Any, Awaitable

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from loguru import logger


class CounterMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()
        self.counter = 0

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        self.counter += 1
        data['counter'] = self.counter
        logger.info(data)
        return await handler(event, data)

