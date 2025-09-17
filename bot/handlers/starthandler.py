from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message

import database.requests as rq


router = Router()


@router.message(CommandStart())
async def start(message: Message, bot: Bot) -> None:
    await rq.set_user(message.from_user.id, message.from_user.full_name)
    await bot.send_message(message.from_user.id, f'💄 О, да ты же будущая бьюти-звезда! Замечательно, что ты здесь!\n\nМеня создали, чтобы помочь тебе растить аудиторию, делать огненный контент и зарабатывать на своем призвании.\n\nВ моем меню ты найдешь курсы и гайды, которые перевернут твой блог. Жми на кнопку и погнали! 🚀')
    
