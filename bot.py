import logging
import os
from db import select_categories
import replies
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackQueryHandler, ConversationHandler)
from dotenv import load_dotenv

logger = logging
logger.basicConfig(filename='bot.log', level=logging.INFO,
                   format='%(asctime)s %(levelname)s - %(message)s')

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHOOSING_CATEGORY, DELETING = range(2)


def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Разговор добавления расхода.
    entry_add_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex(r'^(\d+)$'), replies.get_amount)],
        states={
            CHOOSING_CATEGORY: [
                MessageHandler(Filters.text(select_categories()),
                               replies.add_entry),
                MessageHandler(Filters.regex(r'(?i)^(?!ОТМЕНА$).+'),
                               replies.wrong_category)],
        },
        fallbacks=[MessageHandler(Filters.regex(r'^ОТМЕНА$'), replies.cancel)],
    )

    # Разговор удаления расходов
    entry_delete_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', replies.delete_entry)],
        states={
            DELETING: [CallbackQueryHandler(replies.delete,
                       pattern=r'^(\d+)$')],
        },
        fallbacks=[CallbackQueryHandler(replies.cancel_delete)],
    )

    dispatcher.add_handler(entry_add_conv_handler)
    dispatcher.add_handler(entry_delete_conv_handler)
    dispatcher.add_handler(CommandHandler('start', replies.start))
    dispatcher.add_handler(CommandHandler('help', replies.start))
    dispatcher.add_handler(CommandHandler('today', replies.today_entries))
    dispatcher.add_handler(CommandHandler('month', replies.month_entries))
    dispatcher.add_handler(CommandHandler('last', replies.last_entries))
    updater.start_polling()


if __name__ == '__main__':
    main()
