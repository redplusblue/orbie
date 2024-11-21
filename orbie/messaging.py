import asyncio

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from conversation_agent import chat_groq, secret, config
from orbie.conversation_agent import search_groq
from web_search import search

# Load the secret values
BOT_TOKEN = secret["TELEGRAM_BOT_TOKEN"]
AUTHORIZED_USERS = secret["TELEGRAM_AUTHORIZED_USERS"]
# Limits
SEARCH_LIMIT = config["search"]["token_limit"]

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
        await update.message.reply_text(f"Unfortunately, I couldn't understand that message.")
        print("Error in chat command: \n\n", e)

@restricted
async def web_search(update: Update, context: CallbackContext):
    """
    Search the web, using LLM & SearXNG
    :param update: The update object.
    :param context: The context object.
    :return:
    """
    user_message = ' '.join(context.args)
    user_name = update.effective_user.first_name
    if not user_message:
        await update.message.reply_text("Please include a search query. Example: /search How to make a cake?")
        return
    # user_message should not exceed 10k tokens
    if len(user_message.split()) > SEARCH_LIMIT:
        await update.message.reply_text(f"Search query exceeds the token limit of {SEARCH_LIMIT}.")
        return

    try:
        search_result = search(user_message)
        llm_result = search_groq(f"{user_name} asked for " + search_result)
        await update.message.reply_text(llm_result)
    except Exception as e:
        await update.message.reply_text(f"Sorry, I couldn't find any results for that query.")
        print("Error in search command: \n\n", e)

@restricted
async def generic_response(update: Update, context: CallbackContext):
    """
    Handle all text messages with a generic response.
    :param update: The update object.
    :param context: The context object.
    :return: None
    """
    await update.message.reply_text("Please use a valid command or message, or use /help for more information.")

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
    /search - Search the web (Powered by SearXNG)
    /help - Get help on commands
    """
    await update.message.reply_text(help_text)

# Send a message to users
async def send_msg(user_id, message):
    """
    Send a message to a user from a non-async context.
    :param user_id: The user ID.
    :param message: The message to send.
    :return: True if the message was sent successfully, False otherwise.
    """
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        await application.bot.send_message(chat_id=AUTHORIZED_USERS[user_id], text=message)
        return True
    except Exception as e:
        print(e)
        return False

# TODO:
def detect_command(user_message):
    """
    Detect the command based on the user's message.
    :param user_message: The user's message.
    :return: The detected command.
    """
    if "/chat" in user_message:
        return "chat"
    elif "/search" in user_message:
        return "search"
    else:
        return "generic_response"

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
    application.add_handler(CommandHandler("search", web_search))

    # Message handlers TODO: Implement History (Optimize tokens) and then make \chat the default response.
    application.add_handler(MessageHandler(filters.TEXT, generic_response))

    # Fallback for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, generic_response))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()

