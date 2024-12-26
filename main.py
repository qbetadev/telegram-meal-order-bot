from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

# Меню завтрака
breakfast_menu = {
    "1": {"name": "Овсянка", "price": 150},
    "2": {"name": "Яичница с беконом", "price": 200},
    "3": {"name": "Блины", "price": 180},
    "4": {"name": "Смузи", "price": 120},
}

# Команды клавиатуры
commands = {
    "/menu": "Посмотреть меню",
    "/checkout": "Завершить заказ",
}

# Хранилище заказов
user_orders = {}

async def start(update, context):
    # Создание кнопок
    keyboard = [["Посмотреть меню"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Добро пожаловать! Выберите команду из меню ниже:",
        reply_markup=reply_markup,
    )
    # Здесь и далее print используется для отображения в терминал ввода пользователя в боте
    print("start")


async def menu(update, context):
    # Отображение меню завтраков
    keyboard = [
        [f"{item['name']} - {item['price']}₽"] for item in breakfast_menu.values()
    ]
    keyboard.append(["Завершить заказ"])  # Добавляем кнопку для завершения заказа
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите блюдо из меню", reply_markup=reply_markup)
    print("menu")

async def button_handler(update, context):
    # Обработка выбора блюда из меню
    query = update.callback_query
    await query.answer()

    item_id = query.data
    item = breakfast_menu.get(item_id)

    if not item:
        query.edit_message_text(text="Произошла ошибка. Попробуйте снова.")
        return

    user_id = query.from_user.id
    user_orders.setdefault(user_id, []).append(item)
    print(item)

    await query.edit_message_text(
        text=f"Вы добавили '{item['name']}' в заказ! Чтобы завершить, введите /checkout."
    )

async def handle_user_input(update, context):
    user_message = update.message.text
    user_id = update.message.from_user.id

    # Проверка вызова команды /menu
    if user_message == commands["/menu"]:
        await menu(update, context)

    # Проверка вызова команды /checkout
    if user_message == commands["/checkout"]:
        await checkout(update, context)

    # Проверка выбора блюда
    for item in breakfast_menu.values():
        if user_message.startswith(item["name"]):
            # Сохраняем выбор пользователя
            user_orders.setdefault(user_id, []).append(item)
            await update.message.reply_text(f"Вы выбрали: {item['name']} за {item['price']}₽")

            # Печать выбора в терминал
            print(f"User {user_id} selected: {item['name']} - {item['price']}₽")
            return

# Функция оформления заказа
async def checkout(update, context):
    user_id = update.message.from_user.id
    orders = user_orders.get(user_id, [])

    if not orders:
        await update.message.reply_text("Ваш заказ пуст. Выберите блюдо, используя меню.")
        return

    # Формируем список блюд и общую стоимость
    order_summary = "\n".join([f"{item['name']} - {item['price']}₽" for item in orders])
    total_price = sum(item['price'] for item in orders)

    await update.message.reply_text(
        f"Ваш заказ:\n{order_summary}\n\nИтого: {total_price}₽\nСпасибо за ваш заказ!"
    )

    # Очищаем заказ после оформления
    user_orders[user_id] = []

def main():
    application = Application.builder().token("7499081948:AAGkCVDkOIQZLhbfQXIz13Hrbx9z4XvoNpQ").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("checkout", checkout))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT, handle_user_input))
    application.run_polling()

if __name__ == "__main__":
    main()