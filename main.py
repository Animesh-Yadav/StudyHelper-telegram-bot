from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Replace with your actual bot token
BOT_TOKEN = "7955835419:AAGjxTFvtAUckg-yVfxxphPWhrEksPk5sZU"


# Admin ID (replace with your Telegram user ID)
ADMIN_ID = 6645404238  # TODO: Replace this with your real Telegram user ID

# Data for the bot flow
classes = ['6', '7', '8', '9', '10', '11', '12']
subjects = {
    '6': ['Math', 'Science', 'English', 'Social', 'Hindi'],
    '7': ['Math', 'Science', 'English', 'Social', 'Hindi'],
    '8': ['Math', 'Science', 'English', 'Social', 'Hindi'],
    '9': ['Math', 'Science', 'English', 'Social', 'Hindi'],
    '10': ['Math', 'Science', 'English', 'Social'],
    '11': ['Physics', 'Chemistry', 'Maths', 'Biology'],
    '12': ['Physics', 'Chemistry', 'Maths', 'Biology']
}
years = ['2020', '2021', '2022', '2023', '2024']

# Temporary user state
user_data = {}

# For tracking stats
user_logs = []


def build_keyboard(options, add_back=True):
    keyboard = [[KeyboardButton(opt)] for opt in options]
    if add_back:
        keyboard.append([KeyboardButton("🔙 Back")])
    keyboard.append([KeyboardButton("/start"), KeyboardButton("☰ Menu")])
    return keyboard

def main_menu():
    return [[KeyboardButton("📚 Start")], [KeyboardButton("/admin")]]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data[chat_id] = {'step': 'menu'}
    await update.message.reply_text("👋 Welcome! Please choose an option:", reply_markup=ReplyKeyboardMarkup(main_menu(), resize_keyboard=True))


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        total_users = len(user_data)
        total_requests = len(user_logs)
        last_requests = '\n'.join(user_logs[-5:]) or "No logs yet."
        msg = f"👮 Admin Panel\n\nTotal Users: {total_users}\nTotal Requests: {total_requests}\n\nLast 5 Requests:\n{last_requests}"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ You are not authorized to access this command.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text
    data = user_data.get(chat_id, {'step': 'menu'})

    if text == "/start":
        await start(update, context)
        return

    if text == "/admin":
        await admin(update, context)
        return

    if text == "📚 Start" or text == "☰ Menu":
        data = {'step': 'class'}
        keyboard = build_keyboard(classes, add_back=False)
        await update.message.reply_text("📚 Please select your class:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        user_data[chat_id] = data
        return

    # Back button logic
    if text == "🔙 Back":
        if data['step'] == 'subject':
            data.pop('class', None)
            data['step'] = 'class'
            keyboard = build_keyboard(classes, add_back=False)
            await update.message.reply_text("📚 Please select your class:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        elif data['step'] == 'year':
            data.pop('subject', None)
            data['step'] = 'subject'
            cls = data['class']
            keyboard = build_keyboard(subjects[cls], add_back=True)
            await update.message.reply_text("📘 Please select your subject:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        else:
            data = {'step': 'menu'}
            await update.message.reply_text("🔁 Back to main menu. Choose an option:", reply_markup=ReplyKeyboardMarkup(main_menu(), resize_keyboard=True))
        user_data[chat_id] = data
        return

    # Class selection
    if data['step'] == 'class':
        if text in classes:
            data['class'] = text
            data['step'] = 'subject'
            keyboard = build_keyboard(subjects[text])
            await update.message.reply_text("📘 Please select your subject:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        else:
            keyboard = build_keyboard(classes, add_back=False)
            await update.message.reply_text("❗ Invalid class. Please select from the options.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # Subject selection
    elif data['step'] == 'subject':
        if text in subjects.get(data.get('class'), []):
            data['subject'] = text
            data['step'] = 'year'
            keyboard = build_keyboard(years)
            await update.message.reply_text("📅 Please select the year:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        else:
            cls = data['class']
            keyboard = build_keyboard(subjects[cls])
            await update.message.reply_text("❗ Invalid subject. Please select from the options.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    # Year selection
    elif data['step'] == 'year':
        if text in years:
            data['year'] = text
            cls = data['class']
            subject = data['subject'].lower()
            year = data['year']
            url = f"https://yourwebsite.com/class-{cls}/{subject}/{year}.pdf"
            await update.message.reply_text(f"📄 Here is your paper:\n🔗 {url}")
            user_logs.append(f"Class {cls}, Subject {subject}, Year {year}, User {chat_id}")
            user_data.pop(chat_id, None)
        else:
            keyboard = build_keyboard(years)
            await update.message.reply_text("❗ Invalid year. Please select from the options.", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

    user_data[chat_id] = data


# Main function
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
