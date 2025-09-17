from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.requests import select_gaid, select_kurs

admincompkeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить гайд', callback_data='keyboardaddgaid')], [InlineKeyboardButton(text='Добавить курс', callback_data='keyboardaddkurs')], [InlineKeyboardButton(text='Удалить гайд', callback_data='keyboard_delete_gaid')], [InlineKeyboardButton(text='Удалить курс', callback_data='keyboard_delete_kurs')],
    [InlineKeyboardButton(text='Статистика', callback_data='keyboardstatistika')], [InlineKeyboardButton(text='Рассылка', callback_data='keyboardrassilka')]
])


list = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Курсы', callback_data='sendkurs')],
    [InlineKeyboardButton(text='Гайды', callback_data='sendgaids')],
    [InlineKeyboardButton(text='Ваше сообщение', callback_data='custom_message')]
])


payment_keyboard_gaid = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплата ⭐️', callback_data='stars_gaid', pay=True)]
], resize_keyboard=True)


payment_keyboard_kurs = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплата ⭐️', callback_data='stars_kurs', pay=True)]
], resize_keyboard=True)


async def selectkeyboardgaid():
    all_gaid = await select_gaid()
    keyboard = InlineKeyboardBuilder()
    for gaid in all_gaid:
        keyboard.add(InlineKeyboardButton(text=gaid.name_fail_gaid, callback_data=f"selectgaid_{gaid.name_fail_gaid}"))
    return keyboard.adjust(2).as_markup()


async def selectkeyboardkurs():
    all_kurs = await select_kurs()
    keyboard = InlineKeyboardBuilder()
    for kurs in all_kurs:
        keyboard.add(InlineKeyboardButton(text=kurs.name_fail_kurs, callback_data=f"selectkurs_{kurs.name_fail_kurs}"))
    return keyboard.adjust(2).as_markup()


async def sendkeyboardkurs():
    all_kurs = await select_kurs()
    keyboard = InlineKeyboardBuilder()
    for kurs in all_kurs:
        keyboard.add(InlineKeyboardButton(text=kurs.name_fail_kurs, callback_data=f"sendkurs_{kurs.name_fail_kurs}"))
    return keyboard.adjust(2).as_markup()


async def sendkeyboardgaid():
    all_gaid = await select_gaid()
    keyboard = InlineKeyboardBuilder()
    for gaid in all_gaid:
        keyboard.add(InlineKeyboardButton(text=gaid.name_fail_gaid, callback_data=f"sendgaid_{gaid.name_fail_gaid}"))
    return keyboard.adjust(2).as_markup()


async def delit_keyboard_gaid():
    all_gaid = await select_gaid()
    keyboard = InlineKeyboardBuilder()
    for gaid in all_gaid:
        keyboard.add(InlineKeyboardButton(text=gaid.name_fail_gaid, callback_data=f"delitg_{gaid.name_fail_gaid}"))
    return keyboard.adjust(2).as_markup()


async def delit_keyboard_kurs():
    all_kurs = await select_kurs()
    keyboard = InlineKeyboardBuilder()
    for kurs in all_kurs:
        keyboard.add(InlineKeyboardButton(text=kurs.name_fail_kurs, callback_data=f"delitk_{kurs.name_fail_kurs}"))
    return keyboard.adjust(2).as_markup()
