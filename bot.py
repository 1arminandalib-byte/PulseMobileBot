import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8550048983:AAEYmfJknLYQXNh9iFm4Be5C766w0kCZN5w"
ADMIN_ID = 839797458
CHANNEL_SUBSCRIPTIONS = "https://t.me/+9VSnx-4S0GQ0MzE0"
CHANNEL_PAYMENT = "https://t.me/+zERTZanikOY0MDg0"

user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data_store and user_data_store[user_id].get('full_name'):
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(
            "👋 به ربات پالس موبایل خوش اومدی!\n\nلطفاً نام و فامیل خودت رو بفرست:"
        )
        context.user_data['waiting_for_name'] = True

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_name'):
        user_id = update.effective_user.id
        full_name = update.message.text
        if user_id not in user_data_store:
            user_data_store[user_id] = {}
        user_data_store[user_id]['full_name'] = full_name
        context.user_data['waiting_for_name'] = False
        await update.message.reply_text(
            f"✅ نام شما ثبت شد: {full_name}\n\n"
            "📱 حالا می‌تونی شماره تماس خودت رو بفرستی (اختیاری).\nاگه نمی‌خوای، فقط /skip رو بزن."
        )
        context.user_data['waiting_for_phone'] = True

async def skip_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_phone'):
        context.user_data['waiting_for_phone'] = False
        await after_registration(update, context)

async def after_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    name = user_data_store[user_id].get('full_name', 'نامشخص')
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 کاربر جدید ثبت نام کرد!\n👤 نام: {name}\n🆔 آیدی: {user_id}"
    )
    await show_main_menu(update, context)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 اشتراک‌ها - راهنما", callback_data="guide_sub")],
        [InlineKeyboardButton("💳 روش پرداخت - راهنما", callback_data="guide_pay")],
        [InlineKeyboardButton("📤 ارسال فیش", callback_data="send_receipt")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("منوی اصلی:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "guide_sub":
        await query.edit_message_text(
            "📢 راهنمای انتخاب اشتراک:\n\nبا کلیک روی لینک زیر وارد کانال اشتراک‌ها بشید.\n\n👇 لینک کانال اشتراک‌ها:"
        )
        await query.message.reply_text(CHANNEL_SUBSCRIPTIONS)
        
    elif query.data == "guide_pay":
        await query.edit_message_text(
            "💰 راهنمای پرداخت:\n\nبا کلیک روی لینک زیر وارد کانال روش‌های پرداخت بشید.\n\n👇 لینک کانال پرداخت:"
        )
        await query.message.reply_text(CHANNEL_PAYMENT)
        
    elif query.data == "send_receipt":
        context.user_data['waiting_for_receipt'] = True
        await query.edit_message_text(
            "📸 لطفاً تصویر فیش واریزی خودت رو ارسال کن.\n\nپس از بررسی توسط ادمین، اشتراک فعال میشه ✅"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_receipt'):
        user = update.effective_user
        photo = update.message.photo[-1]
        user_info = user_data_store.get(user.id, {})
        full_name = user_info.get('full_name', 'ثبت نشده')
        
        caption = f"📸 فیش جدید\n👤 نام: {full_name}\n🆔 آیدی: {user.id}\n\nبرای تایید: /approve {user.id}"
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo.file_id, caption=caption)
        await update.message.reply_text("✅ فیش شما دریافت شد. پس از تایید، اشتراک برات ارسال میشه.")
        context.user_data['waiting_for_receipt'] = False

async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی ندارید!")
        return
    try:
        user_id = int(context.args[0])
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 اشتراک شما تایید شد!\n\n{CHANNEL_SUBSCRIPTIONS}"
        )
        await update.message.reply_text(f"✅ اشتراک برای کاربر {user_id} ارسال شد.")
    except:
        await update.message.reply_text("❌ استفاده: /approve آیدی_کاربر")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("skip", skip_phone))
    app.add_handler(CommandHandler("approve", admin_approve))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("ربات روشن شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
