from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import asyncio
import marzban_all_acyncio



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
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,resize_keyboard=True)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

# Функция для обработки нажатия кнопки "Магазин"
async def shop(update: Update, context):

    keyboard = [
        [InlineKeyboardButton("🇫🇷", callback_data='fr')],
        [InlineKeyboardButton("🇳🇱", callback_data='nl')],
        [InlineKeyboardButton("🇩🇪", callback_data='de')],
        [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите страну:', reply_markup=reply_markup)


# Функция для обработки выбора ключа
async def button(update: Update, context):
    query = update.callback_query
    await query.answer()

    #Франция
    if query.data == 'fr':
            key_keyboard = [
                [InlineKeyboardButton("🔧Пробный ключ", callback_data='testfr')],
                [InlineKeyboardButton("💰Купить ключ", callback_data='buyfr')],
                [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

            ]
            reply_markup = InlineKeyboardMarkup(key_keyboard)
            await query.edit_message_text('Информация о сервере ⭐️ 🇫🇷 Франция, unlim, 300 руб/мес:\nТип сервера: ♿ MARZBAN VPN\nРейтинг: NA\nPing: 40 ms\nСтоимость: 300 руб/мес.\nТестовый период: 30 мин.\nПолучая ключ вы подтверждаете, что ознакомились и принимаете правила опубликованные на официальном сайте ', reply_markup=reply_markup)

                # Ответ пользователю в зависимости от выбранного ключа

    #Германия
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

    #Нидерланды
    elif query.data == 'nl':
        key_keyboard = [
            [InlineKeyboardButton("🔧Пробный ключ", callback_data='testnl')],
            [InlineKeyboardButton("💰Купить ключ", callback_data='buynl')],
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(key_keyboard)
        await query.edit_message_text('Информация о сервере ⭐️ 🇳🇱 Нидерланды, unlim, 300 руб/мес:\nТип сервера: ♿ MARZBAN VPN\nРейтинг: NA\nPing: 40 ms\nСтоимость: 300 руб/мес.\nТестовый период: 30 мин.\nПолучая ключ вы подтверждаете, что ознакомились и принимаете правила опубликованные на официальном сайте  ', reply_markup=reply_markup)


    #Пробный ключ Франция
    elif query.data == 'testfr':

        base_url = 'url'
        yours_username = 'username'
        yours_password = 'password'
        ssl = True

        client = marzban_all_acyncio.Marzipan(
            url=base_url,
            username=yours_username,
            password=yours_password,
            ssl=ssl
        )
        await client.async_init()
        await client.delet_exp()
        key = await client.get_trial_subscription()

        #Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"Вы получили пробный ключ, его срок действия 30 минут:\n\n"
                                           f"`{key[0]}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](urlinsrtuction)",
                                      parse_mode="MarkdownV2",
            reply_markup=reply_markup)

    #Обычный ключ Франция
    elif query.data == 'buyfr':

        base_url = 'url'
        yours_username = 'username'
        yours_password = 'password'
        ssl = True

        client = marzban_all_acyncio.Marzipan(
            url=base_url,
            username=yours_username,
            password=yours_password,
            ssl=ssl
        )
        await client.async_init()
        await client.delet_exp()
        key = await client.get_subscription()

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Спасибо за покупку, ваш ключ:\n\n"
                                           f"`{key[0]}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](urlinsrtuction)",
                                      parse_mode="MarkdownV2",
            reply_markup=reply_markup)
        await back(update, context)

    #Пробный ключ Нидерланды
    elif query.data == 'testnl':

        base_url = 'url'
        yours_username = 'username'
        yours_password = 'password'
        ssl = True

        client = marzban_all_acyncio.Marzipan(
            url=base_url,
            username=yours_username,
            password=yours_password,
            ssl=ssl
        )
        await client.async_init()
        await client.delet_exp()
        key = await client.get_trial_subscription()

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Вы получили пробный ключ, его срок действия 30 минут:\n\n"
                                           f"`{key[0]}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](urlinsrtuction)",
                                      parse_mode="MarkdownV2",
            reply_markup=reply_markup)
        await back(update, context)

    #Обычный ключи Нидерланды
    elif query.data == 'buynl':

        base_url = 'url'
        yours_username = 'username'
        yours_password = 'password'
        ssl = True

        client = marzban_all_acyncio.Marzipan(
            url=base_url,
            username=yours_username,
            password=yours_password,
            ssl=ssl
        )
        await client.async_init()
        await client.delet_exp()
        key = await client.get_subscription()

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Спасибо за покупку, ваш ключ:\n\n"
                                           f"`{key[0]}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](urlinsrtuction)",
                                      parse_mode="MarkdownV2",
            reply_markup=reply_markup)
        await back(update, context)

    #Тестовый ключ Германия
    elif query.data == 'testde':

        base_url = 'url'
        yours_username = 'username'
        yours_password = 'password'
        ssl = True

        client = marzban_all_acyncio.Marzipan(
            url=base_url,
            username=yours_username,
            password=yours_password,
            ssl=ssl
        )
        await client.async_init()
        await client.delet_exp()
        key = await client.get_trial_subscription()

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Вы получили пробный ключ, его срок действия 30 минут:\n\n"
                                           f"`{key[0]}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](urlinsrtuction)",
                                      parse_mode="MarkdownV2",
            reply_markup=reply_markup)
        await back(update, context)

    #Обычный ключ Германия
    elif query.data == 'buyde':

        base_url = 'url'
        yours_username = 'username'
        yours_password = 'password'
        ssl = True

        client = marzban_all_acyncio.Marzipan(
            url=base_url,
            username=yours_username,
            password=yours_password,
            ssl=ssl
        )
        await client.async_init()
        await client.delet_exp()
        key = await client.get_subscription()

        # Возврат в главное меню
        keyboard = [
            [InlineKeyboardButton("🛒Главное меню", callback_data='back')]

        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=f"Спасибо за покупку, ваш ключ:\n\n"
                                           f"`{key[0]}` \n\n"
                                           f"Если возникли вопросы:\n"
                                           f"[Инструкция по использованию](urlinsrtuction)",
                                      parse_mode="MarkdownV2",
            reply_markup=reply_markup)
        await back(update, context)



    elif query.data == 'back':
        await back(update, context)


#Кнопка Кошелек
async def wallet(update: Update, context):
    keyboard = [
        ['💵Баланс'],
        ['➕Пополнить'],
        ['🛒Главное меню']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Что вас интересует?', reply_markup=reply_markup)

#Кнопка Баланс
async def balance(update: Update, context):
    keyboard = [
        ['🛒Главное меню']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Ваш баланс: 0', reply_markup=reply_markup)

#Кнопка пополнения
async def pay(update: Update, context):
        keyboard = [
            ['СБП'],
            ['Банковская Карта'],
            ['Bitcoin','🔙Назад']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text('Выбери способ пополнения:', reply_markup=reply_markup)


#Назад
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

    application = Application.builder().token("BOTAPI").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", hello))
    application.add_handler(MessageHandler(filters.Regex('^🏬Магазин$'), shop))
    application.add_handler(MessageHandler(filters.Regex('^🪙Кошелек$'), wallet))
    application.add_handler(MessageHandler(filters.Regex('^💵Баланс$'), balance))
    application.add_handler(MessageHandler(filters.Regex('^➕Пополнить$'), pay))
    application.add_handler(MessageHandler(filters.Regex('^🛒Главное меню$'), start))
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
