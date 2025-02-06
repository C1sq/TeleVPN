from pydoc import replace

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import asyncio
import marzban_all_acyncio
import sqldatabase


# Функция старта
async def hello(update: Update, context):
    await update.message.reply_text('Добро пожаловать.')
    await start(update, context)


async def start(update: Update, context):
    keyboard = [
        ['🏬Магазин'],
        ['🔑Ключи'],
        ['🪙Кошелек']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)


# Функция для обработки нажатия кнопки "Магазин"
async def shop(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("🇫🇷", callback_data='fr')],
        [InlineKeyboardButton("🇩🇪", callback_data='de')],
        [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите страну:', reply_markup=reply_markup)


# Функция для обработки выбора ключа
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Франция
    if query.data == 'fr':
        key_keyboard = [
            [InlineKeyboardButton("🔧Пробный ключ", callback_data='testfr')],
            [InlineKeyboardButton("💰Купить ключ", callback_data='buyfr')],
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(key_keyboard)
        await query.edit_message_text(
            'Информация о сервере ⭐️ 🇫🇷 Франция, unlim, 300 руб/мес:\nТип сервера: ♿ MARZBAN VPN\nРейтинг: NA\nPing: 40 ms\nСтоимость: 300 руб/мес.\nТестовый период: 30 мин.\nПолучая ключ вы подтверждаете, что ознакомились и принимаете правила опубликованные на официальном сайте ',
            reply_markup=reply_markup)

        # Ответ пользователю в зависимости от выбранного ключа

    # Германия
    elif query.data == 'de':
        key_keyboard = [
            [InlineKeyboardButton("🔧Пробный ключ", callback_data='testde')],
            [InlineKeyboardButton("💰Купить ключ", callback_data='buyde')],
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(key_keyboard)
        await query.edit_message_text(
            'Информация о сервере ⭐️ 🇩🇪 Германия, unlim, 300 руб/мес:\nТип сервера: ♿ MARZBAN VPN\nРейтинг: NA\nPing: 40 ms\nСтоимость: 300 руб/мес.\nТестовый период: 30 мин.\nПолучая ключ вы подтверждаете, что ознакомились и принимаете правила опубликованные на официальном сайте ',
            reply_markup=reply_markup)

    # Пробный ключ Франция
    elif query.data == 'testfr':

        await marzban_all_acyncio.France.async_init()
        await marzban_all_acyncio.France.delete_exp()
        user_id = update.effective_user.id

        key = await marzban_all_acyncio.France.get_trial_subscription(telegram_id=str(user_id), param='france')
        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Вы получили пробный ключ, его срок действия 30 минут:\n\n"
            f"`{key}` \n\n"
            f"Если возникли вопросы:\n"
            f"[Инструкция по использованию](https://telegra.ph/Instrukciya-po-ispolzovaniyu-klyuchej-01-31)",
            parse_mode="MarkdownV2",
            reply_markup=reply_markup)


    # Обычный ключ Франция
    elif query.data == 'buyfr':

        await marzban_all_acyncio.France.async_init()
        await marzban_all_acyncio.France.delete_exp()
        user_id = update.effective_user.id

        key = await marzban_all_acyncio.France.get_subscription(telegram_id=str(user_id), param='france')

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Спасибо за покупку, ваш ключ:\n\n"
                                           f"`{key}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](https://telegra.ph/Instrukciya-po-ispolzovaniyu-klyuchej-01-31)",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)

    # Тестовый ключ Германия
    elif query.data == 'testde':

        await marzban_all_acyncio.Germany.async_init()
        await marzban_all_acyncio.Germany.delete_exp()
        user_id = update.effective_user.id

        key = await marzban_all_acyncio.Germany.get_trial_subscription(telegram_id=str(user_id), param='germany')

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Вы получили пробный ключ, его срок действия 30 минут:\n\n"
                                           f"`{key}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](https://telegra.ph/Instrukciya-po-ispolzovaniyu-klyuchej-01-31)",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)

    # Обычный ключ Германия
    elif query.data == 'buyde':

        await marzban_all_acyncio.Germany.async_init()
        await marzban_all_acyncio.Germany.delete_exp()
        user_id = update.effective_user.id

        key = await marzban_all_acyncio.Germany.get_subscription(telegram_id=str(user_id), param='germany')

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Спасибо за покупку, ваш ключ:\n\n"
                                           f"`{key}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](https://telegra.ph/Instrukciya-po-ispolzovaniyu-klyuchej-01-31)",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)



    elif query.data == 'back':
        await back(update, context)

    elif query.data == 'key3':
        user_id = update.effective_user.id
        keyinfo = await marzban_all_acyncio.get_link(telegram_id=str(user_id))
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Ваш ключ:\n\n"
                                           f"`{keyinfo[2]}` \n\n"
                                           f"Если возникли вопросы:\n",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)

    elif query.data == 'key4':

        user_id = update.effective_user.id

        keyinfo = await marzban_all_acyncio.get_link(telegram_id=str(user_id))

        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Ваш ключ:\n\n"
                                           f"`{keyinfo[3]}` \n\n"
                                           f"Если возникли вопросы:\n",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)

    elif query.data == 'key5':

        user_id = update.effective_user.id

        keyinfo = await marzban_all_acyncio.get_link(telegram_id=str(user_id))

        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Ваш ключ:\n\n"
                                           f"`{keyinfo[4]}` \n\n"
                                           f"Если возникли вопросы:\n",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)

    elif query.data == 'key6':

        user_id = update.effective_user.id

        keyinfo = await marzban_all_acyncio.get_link(telegram_id=str(user_id))

        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Ваш ключ:\n\n"
                                           f"`{keyinfo[5]}` \n\n"
                                           f"Если возникли вопросы:\n",
                                      parse_mode="MarkdownV2",
                                      reply_markup=reply_markup)


# Кнопка Кошелек
async def wallet(update: Update, context):
    keyboard = [
        ['💵Баланс'],
        ['➕Пополнить'],
        ['🛒Главное меню']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Что вас интересует?', reply_markup=reply_markup)


# Кнопка Баланс
async def balance(update: Update, context):
    keyboard = [
        ['🛒Главное меню']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Ваш баланс: 0', reply_markup=reply_markup)


async def mykey(update: Update, context):

    base_url = 'https://domkrat.linkpc.net:11445'
    yours_username = 'admin1'
    yours_password = 'df61f27e889e5b8307c3d7affd63b7cf'
    ssl = True

    client = marzban_all_acyncio.Marzipan(
        url=base_url,
        username=yours_username,
        password=yours_password,
        ssl=ssl
    )
    await client.async_init()

    user_id = update.effective_user.id
    keyinfo = await marzban_all_acyncio.get_link(telegram_id=str(user_id))

    if keyinfo is not None:
        keyboard = [
            [InlineKeyboardButton(f"Test ND", callback_data='key1')],
            [InlineKeyboardButton(f"ND", callback_data='key2')],
            [InlineKeyboardButton(f"🇫🇷 Пробный ключ 🇫🇷", callback_data='key3')],
            [InlineKeyboardButton(f"🇫🇷", callback_data='key4')],
            [InlineKeyboardButton(f"🇩🇪 Пробный ключ 🇩🇪", callback_data='key5')],
            [InlineKeyboardButton(f"🇩🇪", callback_data='key6')],
        ]
        Akeyboard = [
        ]
        Bkeyboard = [[InlineKeyboardButton("🛒Главное меню", callback_data='back')]]

        for i in range(len(keyinfo)):

            if keyinfo[i] is not None:
                Akeyboard.append(keyboard[i])
        Akeyboard = Akeyboard + Bkeyboard
        reply_markup = InlineKeyboardMarkup(Akeyboard)
        await update.message.reply_text('Выберите ключ:', reply_markup=reply_markup)
    else:
        Bkeyboard = [[InlineKeyboardButton("🛒Главное меню", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(Bkeyboard)
        await update.message.reply_text('У вас нет ключей:', reply_markup=reply_markup)


# Кнопка пополнения
async def pay(update: Update, context):
    keyboard = [
        ['СБП'],
        ['Банковская Карта'],
        ['Bitcoin', '🔙Назад']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Выбери способ пополнения:', reply_markup=reply_markup)


# Назад
async def back(update: Update, context):
    keyboard = [

        ['🏬Магазин'],
        ['🔑Ключи'],
        ['🪙Кошелек']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.callback_query.message.reply_text('Выберите опцию:', reply_markup=reply_markup)
    await update.callback_query.answer()


# Основная функция для запуска бота
def main():
    application = Application.builder().token("APIBOT").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", hello))
    application.add_handler(MessageHandler(filters.Regex('^🏬Магазин$'), shop))
    application.add_handler(MessageHandler(filters.Regex('^🪙Кошелек$'), wallet))
    application.add_handler(MessageHandler(filters.Regex('^🔑Ключи$'), mykey))
    application.add_handler(MessageHandler(filters.Regex('^💵Баланс$'), balance))
    application.add_handler(MessageHandler(filters.Regex('^➕Пополнить$'), pay))
    application.add_handler(MessageHandler(filters.Regex('^🛒Главное меню$'), start))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
