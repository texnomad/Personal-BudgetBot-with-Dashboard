import logging
import sqlite3
import time
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Путь к SQLite базе данных (настройте под вашу систему)
DB_PATH = r"Budget_DB.db"  # можно использовать относительный путь

# Токен вашего Telegram-бота (замените на свой)
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"

def append_to_sqlite(date_str, amount, category, description, max_retries=5, retry_delay=0.2):
    """
    Добавляет запись в SQLite базу данных.
    :param date_str: Дата в формате 'YYYY-MM-DD'
    :param amount: Сумма (число)
    :param category: Категория
    :param description: Описание
    :return: True при успехе, False при ошибке
    """
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                comment TEXT
            )
            """)

            cursor.execute(
                "INSERT INTO records (date, amount, category, comment) VALUES (?, ?, ?, ?)",
                (date_str, amount, category, description)
            )

            conn.commit()
            conn.close()
            logger.info(f"Данные успешно записаны в БД: {date_str}, {amount}, {category}, {description}")
            return True

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                logger.warning(f"База данных заблокирована, попытка {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay)
                continue
            else:
                logger.error(f"Неизвестная ошибка SQLite: {e}")
                break
        except Exception as e:
            logger.error(f"Ошибка при записи в БД: {e}")
            break
    else:
        logger.error("Не удалось записать в БД: превышено количество попыток из-за блокировки.")
    return False

async def start(update: Update, context) -> None:
    await update.message.reply_text(
        "Привет! Отправь данные в формате:\n"
        "• категория, сумма\n"
        "• категория, сумма, описание\n\n"
        "Доходы указывайте с минусом (например: зп, -50000)"
    )

async def handle_message(update: Update, context) -> None:
    try:
        message_text = update.message.text.strip()
        logger.info(f"Получено сообщение: {message_text}")

        parts = [part.strip() for part in message_text.split(",")]
        if len(parts) not in (2, 3):
            await update.message.reply_text(
                "Неверный формат. Используйте:\n"
                "категория, сумма\n"
                "или\n"
                "категория, сумма, описание"
            )
            return

        if len(parts) == 2:
            category, amount = parts
            description = ""
        else:
            category, amount, description = parts

        try:
            amount = float(amount)
        except ValueError:
            await update.message.reply_text("Сумма должна быть числом.")
            return

        sqlite_date = datetime.now().strftime("%Y-%m-%d")
        success = append_to_sqlite(sqlite_date, amount, category, description)

        if success:
            await update.message.reply_text("✅ Данные успешно записаны в базу!")
        else:
            await update.message.reply_text("❌ Ошибка записи в базу. Попробуйте позже.")

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла неожиданная ошибка.")

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()
    logger.info("Бот запущен.")

if __name__ == "__main__":
    main()