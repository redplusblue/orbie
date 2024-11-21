import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from conversation_agent import chat_groq

with open("../config/secrets.json", "r") as secrets_file:
    secret = json.load(secrets_file)

BOT_TOKEN = secret["TELEGRAM_BOT_TOKEN"]
AUTHORIZED_USERS = secret["TELEGRAM_AUTHORIZED_USERS"]

def restricted(func):
    """
    Decorator to restrict bot access to authorized users.
    :param: The function to be decorated.
    :return: The wrapped function.
    """
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in AUTHORIZED_USERS:
            await update.message.reply_text("You are not authorized to use this bot, please contact orbie@samirkabra.com for access.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped

@restricted
async def start(update: Update, context: CallbackContext):
    """
    Start command handler.
    :param update: The update object.
    :param context: The context object.
    :return: None
    """
    await update.message.reply_text("Hello! I'm Orbie, your AI assistant. Use /chat to start chatting or /help for more commands.")

@restricted
async def chat(update: Update, context: CallbackContext):
    """
    Chat command handler.
    :param update: The update object.
    :param context: The context object.
    :return: None
    """
    user_message = ' '.join(context.args)  # Get the message text after the command
    if not user_message:
        await update.message.reply_text("Please include a message to chat. Example: /chat How are you?")
        return

    try:
        # Call the AI inference function from conversation_agent
        ai_response = chat_groq(user_message, "pookie")
        await update.message.reply_text(ai_response)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

@restricted
async def unknown(update: Update, context: CallbackContext):
    """
    Handle unknown commands.
    :param update: The update object.
    :param context: The context object.
    :return: None
    """
    await update.message.reply_text("Sorry, I didn't understand that command.")

async def help(update: Update, context: CallbackContext):
    """
    Help command handler.
    :param update: The update object.
    :param context: The context object.
    :return: None
    """
    help_text = """
    Available commands:
    /start - Start Orbie
    /chat - Chat with Orbie (Powered by LlaMA)
    /help - Get help on commands
    """
    await update.message.reply_text(help_text)

def main():
    """
    Main function to start the bot.
    :return: None
    """
    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat", chat))

    # Fallback for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()