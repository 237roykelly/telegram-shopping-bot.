from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# States
SELECT_COUNTRY, SELECT_CATEGORY, SELECT_QUANTITY, SHOW_PRICE, ASK_ADDRESS, PAYMENT_PROOF = range(6)

# Supported countries and their languages
country_lang = {
    '🇩🇪': 'de', '🇮🇹': 'it', '🇳🇱': 'nl', '🇷🇴': 'ro',
    '🇹🇷': 'tr', '🇺🇸': 'en', '🇫🇷': 'fr'
}

category_prices = {
    '💳cloned cards💳': ['€300', '€500', '€1000', '€5000'],
    '🪪ID cards🪪': ['€1500 (min deposit €1000)'],
    '🪪Drivers license🪪': ['€1000 (min deposit €700)'],
    '💶Bills💶': ['€300', '€500', '€1000', '€5000']
}

bitcoin_address = "bitcoin:1EqfhYsqgcwPb8TfG4T2tm7XeRiMutsdPj"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton(c) for c in country_lang.keys()]]
    await update.message.reply_text("Which country are you from?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_COUNTRY

async def select_country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = update.message.text
    user_data['country'] = country
    keyboard = [[KeyboardButton("💳cloned cards💳"), KeyboardButton("🪪ID cards🪪")], [KeyboardButton("🪪Drivers license🪪"), KeyboardButton("💶Bills💶")]]
    await update.message.reply_text("What would you like to shop?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_CATEGORY

async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    user_data['category'] = category
    await update.message.reply_text(f"How many {category} would you like to buy? (Enter a number)")
    return SELECT_QUANTITY

async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quantity = update.message.text
    user_data['quantity'] = quantity
    category = user_data['category']
    prices = category_prices.get(category, [])
    await update.message.reply_text(f"The prices for {category} are:\n" + "\n".join(prices))
    await update.message.reply_text(f"You can pay via Bitcoin.com\nSend to:\n{bitcoin_address}")
    await update.message.reply_text("Please provide your shipping address.")
    return ASK_ADDRESS

async def ask_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text
    user_data['address'] = address
    await update.message.reply_text("Upload a screenshot of your Bitcoin payment.")
    return PAYMENT_PROOF

async def payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("Thank you! Your order is being processed. For help, contact @Leopold_MMM.")
        # Forward image to admin later
    else:
        await update.message.reply_text("Please upload an image of the payment.")
        return PAYMENT_PROOF
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Transaction cancelled.")
    return ConversationHandler.END

app = ApplicationBuilder().token("7819128490:AAEBtbAiHuMpa2YoQToJQdOjaj95Dj6tEgQ").build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SELECT_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_country)],
        SELECT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_category)],
        SELECT_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_quantity)],
        ASK_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_address)],
        PAYMENT_PROOF: [MessageHandler(filters.PHOTO, payment_proof)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

app.add_handler(conv_handler)

if __name__ == '__main__':
    app.run_polling()