import asyncio
import logging
import os
import sys
import io
import locale

from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from handlers.starthandler import router
from database.models import async_main
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.starthandler import start
from utils.commands import set_commands
from admin.handlerauthadmin import authorization_start
from admin.handler_add_data import add_gaid, add_data_name, add_data_photo, add_data_description, add_data_file, add_data_price_star, add_kurs
from admin. handler_delit_data import start_on_delit_gaid, drop_gaid, start_on_delit_kurs, drop_kurs
from handlers.handler_output_data import gaid_start, gaid_select, buy_gaid, successful_payment_gaid, pre_checkout_query_gaid, kurs_start, kurs_select, buy_kurs, successful_payment_kurs, cancel_any_state
from admin.sendall import rassilka, kurs, kurssendall, gaids, gaidsendall
from admin.custom_sendall import function_custom_message, get_custom_message
from utils.file_id_updater import periodic_file_id_update
from admin.statistic import statistica

from aiogram.filters import Command
from admin.handler_add_data import AddDataStates
from admin.custom_sendall import Custom_message


load_dotenv('./.env')

logger = logging.getLogger(__name__)


IS_WEBHOOK = 1

token = os.getenv('TOKEN')
NGINX_HOST = os.getenv('NGINX_HOST') 

# webhook settings
WEBHOOK_HOST = f'https://{NGINX_HOST}'
WEBHOOK_PATH = '/webhook'

# webserver settings
WEBAPP_HOST = '0.0.0.0' 
WEBAPP_PORT = 0000

# Установка UTF-8 кодировки
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Попытка установить локаль UTF-8
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass


bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

storage = MemoryStorage()

dp = Dispatcher(storage=storage)


async def cleanup_old_states():
    """Очистка старых состояний каждые 6 часов"""
    while True:
        try:
            # Здесь можно добавить логику очистки, если используешь Redis
            # или другое хранилище с TTL (time-to-live)
            logger.debug("Запуск очистки старых состояний...")
            # Пока просто ждем, если используешь MemoryStorage
            await asyncio.sleep(6 * 60 * 60)  # 6 часов
        except Exception as e:
            logger.error(f"Ошибка в cleanup_old_states: {e}")
            await asyncio.sleep(60 * 60)  # Ждем час при ошибке
    # while True:
    #     await asyncio.sleep(3600)


async def send_error_notification(bot: Bot, error: Exception):
    """
    Отправляет уведомление администратору об ошибке.
    """
    admin_id = os.getenv('ADMIN_ID')
    if not admin_id:
        logging.error("ADMIN_ID не установлен в .env файле!")
        return
        
    try:
        error_message = (
            "⚠️ <b>Произошла ошибка в боте!</b>\n\n"
            f"<b>Тип ошибки:</b> <code>{type(error).__name__}</code>\n"
            f"<b>Описание:</b> <code>{str(error)[:100]}...</code>\n\n"
            "Проверьте логи для деталей."
        )
        await bot.send_message(admin_id, error_message)
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление об ошибке: {e}")


async def errors_handler(exception: Exception) -> bool:
    """
    Обработчик необработанных исключений.
    Логирует ошибку и отправляет уведомление администратору.
    """
    logging.exception(f"Необработанное исключение в обработчике: {exception}")
    
    try:
        await send_error_notification(bot, exception)
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление об ошибке: {e}")
    
    return True


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=f"{WEBHOOK_HOST}{WEBHOOK_PATH}",
        drop_pending_updates=True
        )
    print(f'Серверы Telegram теперь отправляют обновления на {WEBHOOK_HOST}{WEBHOOK_PATH}. Бот подключен к сети')

async def delete_webhook():
    bot = Bot(token=token) 
    await bot.delete_webhook()
    await bot.session.close()


dp.message.register(start, CommandStart())
dp.message.register(authorization_start, Command(commands='adminsettings'))

dp.callback_query.register(add_gaid, F.data.startswith('keyboardaddgaid'))
dp.message.register(add_data_name, AddDataStates.name)
dp.message.register(add_data_photo, AddDataStates.photo)
dp.message.register(add_data_description, AddDataStates.description)
dp.message.register(add_data_file, AddDataStates.file)
dp.message.register(add_data_price_star, AddDataStates.price_star)

dp.message.register(gaid_start, Command(commands='gaid'))
dp.callback_query.register(gaid_select, F.data.startswith('selectgaid_'))
dp.callback_query.register(buy_gaid, F.data.startswith('stars_gaid'))
dp.pre_checkout_query.register(pre_checkout_query_gaid)
dp.message.register(successful_payment_gaid, F.successful_payment.invoice_payload == 'gaid')
dp.callback_query.register(start_on_delit_gaid, F.data.startswith('keyboard_delete_gaid'))
dp.callback_query.register(drop_gaid, F.data.startswith('delitg_'))


dp.callback_query.register(add_kurs, F.data.startswith('keyboardaddkurs'))


dp.message.register(kurs_start, Command(commands='kurs'))
dp.callback_query.register(kurs_select, F.data.startswith('selectkurs_'))
dp.callback_query.register(buy_kurs, F.data.startswith('stars_kurs'))
dp.message.register(successful_payment_kurs, F.successful_payment.invoice_payload == 'kurs')
dp.message.register(cancel_any_state, Command(commands=['gaid', 'kurs']))
dp.callback_query.register(start_on_delit_kurs, F.data.startswith('keyboard_delete_kurs'))
dp.callback_query.register(drop_kurs, F.data.startswith('delitk_'))


dp.callback_query.register(rassilka, F.data.startswith('keyboardrassilka'))
dp.callback_query.register(kurs, F.data == 'sendkurs')
dp.callback_query.register(kurssendall, F.data.startswith('sendkurs_'))
dp.callback_query.register(gaids, F.data == 'sendgaids')
dp.callback_query.register(gaidsendall, F.data.startswith('sendgaid_'))
dp.callback_query.register(function_custom_message, F.data == 'custom_message')
dp.message.register(get_custom_message, Custom_message.msg_custom)

dp.callback_query.register(statistica, F.data.startswith('keyboardstatistika'))

dp.errors.register(errors_handler)


dp.include_router(router)

async def healthcheck(request: web.Request) -> web.Response:
    """Endpoint для проверки работоспособности бота"""
    return web.Response(text="OK", status=200)

    
async def main() -> None:
    print("Бот запущен! Проверка вебхука...")
    await async_main()
    await set_commands(bot)

    # Запускаем фоновую задачу обновления file_id
    asyncio.create_task(periodic_file_id_update(bot, interval_days=7))

    asyncio.create_task(cleanup_old_states())
    
    if IS_WEBHOOK == 1:
        print("Запуск в режиме WEBHOOK...")

        await bot.delete_webhook()
          
        try:
            await bot.set_webhook(
                url=f"{WEBHOOK_HOST}{WEBHOOK_PATH}",
                drop_pending_updates=True
            )
            print(f"Вебхук установлен на {WEBHOOK_HOST}{WEBHOOK_PATH}")
        except Exception as e:
            print(f"Ошибка при установке вебхука: {e}")
            return

        app = web.Application()
        app.router.add_get('/health', healthcheck)
        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
        await site.start()
        
        print(f"Бот запущен на {WEBHOOK_HOST}")
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            print("\nПолучен сигнал остановки...")
        except Exception as e:
            print(f"\nКритическая ошибка: {e}")
        finally:
            print("Останавливаем бота...")
            await bot.session.close()
            await runner.cleanup()
            print("Бот успешно остановлен")
    else:
        print("Запуск в режиме POLLING...")

        try:
            await bot.delete_webhook(drop_pending_updates=True)
            print("Вебхук удален (если был установлен)")
        except Exception as e:
            print(f"Ошибка при удалении вебхука: {e}")

        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("\nПолучен сигнал остановки...")
        except Exception as e:
            logging.exception("Критическая ошибка в боте:")
            await send_error_notification(bot, e)
            raise
        finally:
            print("Останавливаем бота...")
            await bot.session.close()
            await dp.storage.close()
            print("Бот успешно остановлен")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот был остановлен пользователем")
    