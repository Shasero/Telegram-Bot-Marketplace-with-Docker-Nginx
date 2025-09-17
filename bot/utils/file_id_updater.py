import asyncio
import logging
from aiogram import Bot
from database.requests import get_all_gaids, get_all_kurs, update_gaid_file_id, update_kurs_file_id
from database.models import Gaid, Kurs

logger = logging.getLogger(__name__)

async def check_and_update_file_id(bot: Bot, db_model, get_all_func, update_func, id_attr, file_id_attr, local_path_attr):
    """Общая функция для проверки и обновления file_id для Gaid или Kurs"""
    all_items = await get_all_func()
    logger.info(f"Проверяем {len(all_items.all())} элементов")

    for item in all_items:
        old_file_id = getattr(item, file_id_attr)
        local_file_path = getattr(item, local_path_attr)
        item_name = getattr(item, id_attr)

        logger.info(f"Проверка файла: {item_name}")

        try:
            # Пытаемся скачать файл по старому file_id
            file_info = await bot.get_file(old_file_id)
            logger.info(f"File ID для {item_name} все еще актуален: {file_info.file_id}")
        except Exception as e:
            logger.warning(f"File ID устарел для {item_name}. Ошибка: {e}. Пытаюсь обновить...")
            try:
                # Загружаем файл с диска и получаем новый file_id
                from aiogram.types import FSInputFile
                file_to_upload = FSInputFile(local_file_path)
                message_with_new_file = await bot.send_document(chat_id=bot.id, document=file_to_upload)
                new_file_id = message_with_new_file.document.file_id

                # Обновляем file_id в базе данных
                await update_func(getattr(item, id_attr), new_file_id)
                logger.info(f"File ID для {getattr(item, id_attr)} успешно обновлен!")

                # (Опционально) Можно удалить старое сообщение с файлом, чтобы не засорять чат с ботом
                await bot.delete_message(chat_id=bot.id, message_id=message_with_new_file.message_id)

            except Exception as upload_error:
                logger.error(f"Не удалось обновить file_id для {getattr(item, id_attr)}: {upload_error}")

async def periodic_file_id_update(bot: Bot, interval_days=7):
    """Запускает проверку обновления file_id с заданным интервалом"""
    while True:
        try:
            logger.info("Запуск периодической проверки file_id...")
            await check_and_update_file_id(
                bot, Gaid, get_all_gaids, update_gaid_file_id, 'name_fail_gaid', 'fail_gaid', 'local_path_gaid'
            )
            await check_and_update_file_id(
                bot, Kurs, get_all_kurs, update_kurs_file_id, 'name_fail_kurs', 'fail_kurs', 'local_path_kurs'
            )
        except Exception as e:
            logger.error(f"Критическая ошибка в periodic_file_id_update: {e}")
        
        # Ожидаем заданное количество дней (в секундах)
        await asyncio.sleep(interval_days * 24 * 60 * 60)