import db
from bot import logger
from telegram import (InlineKeyboardMarkup, Update,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import CallbackContext, ConversationHandler


CHOOSING_CATEGORY, DELETING = range(2)
END = ConversationHandler.END


def start(update: Update, _: CallbackContext):
    """"Отправляет сообщение с доступными командами"""
    update.message.reply_text(
        'Бот для учета расходов.\n\n'
        'Введите сумму\n\n'
        'Расходы за текущий день: /today\n'
        'Расходы за текущий месяц: /month\n'
        'Последние 5 расходов: /last\n'
        'Удаление записей: /delete')


def month_entries(update: Update, _: CallbackContext):
    """Отправляет сообщение с расходами за месяц"""
    user_id = update.effective_user.id
    entries = db.select_month(user_id)
    reply = 'Расходы за месяц:\n' + entries.to_text()
    update.message.reply_text(reply)


def today_entries(update: Update, _: CallbackContext):
    """Отправляет сообщение с расходами за сегодня"""
    user_id = update.effective_user.id
    entries = db.select_today(user_id)
    reply = 'Расходы за сегодня\n' + entries.to_text()
    update.message.reply_text(reply)


def last_entries(update: Update, _: CallbackContext):
    """Отправляет сообщение с последними расходами"""
    user_id = update.effective_user.id
    entries = db.select_last(user_id)
    reply = 'Последние расходы:\n' + entries.to_text()
    update.message.reply_text(reply)


def get_amount(update: Update, context: CallbackContext):
    """Получает сумму из чата. Выводит клавиатуру с категориями."""
    context.user_data['amount'] = update.message.text
    keys = db.select_categories().to_keys()
    reply_markup = ReplyKeyboardMarkup(keys, False, True)
    update.message.reply_text(
        'Выберите категорию.', reply_markup=reply_markup)
    return CHOOSING_CATEGORY


def add_entry(update: Update, context: CallbackContext):
    """"Добавляет расход."""
    user_id = update.effective_user.id
    amount = context.user_data['amount']
    category = update.message.text
    db.insert_entry(user_id, amount, category)
    reply = 'Расход добавлен.'
    update.message.reply_text(
        reply, reply_markup=ReplyKeyboardRemove())
    return END


def wrong_category(update: Update, _: CallbackContext):
    """Выводит ошибку ввода категории"""
    keys = db.select_categories().to_keys()
    reply_markup = ReplyKeyboardMarkup(keys, False, True)
    update.message.reply_text(
            'Такой категории нет.\nВыберите категорию.',
            reply_markup=reply_markup)
    return CHOOSING_CATEGORY


def cancel(update: Update, _: CallbackContext):
    """Отменяет ввод категории."""
    update.message.reply_text(
        'Ввод отменен.', reply_markup=ReplyKeyboardRemove())
    return END


def delete_entry(update: Update, _: CallbackContext):
    """Выводит клавиатуру с последними расходами."""
    user_id = update.effective_user.id
    keys = db.select_last(user_id).to_keys()
    if not keys:
        update.message.reply_text('Расходов пока нет.')
        return END

    update.message.reply_text(
        'Нажмите для удаления.',
        reply_markup=InlineKeyboardMarkup(keys))
    return DELETING


def delete(update: Update, _: CallbackContext):
    """Удаляет расход."""
    query = update.callback_query
    query.answer()
    purchase_id = query.data
    db.delete_entry(purchase_id)
    user_id = update.effective_user.id
    keys = db.select_last(user_id).to_keys()
    if not keys:
        query.edit_message_text('Расходов больше нет.')
        return END

    query.edit_message_text(
        'Удалено.\nНажмите для удаления.',
        reply_markup=InlineKeyboardMarkup(keys))
    return DELETING


def cancel_delete(update: Update, _: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Режим удаления отключен.')
    return END
