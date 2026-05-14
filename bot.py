import os
import json
import random
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Files for data storage
QUOTES_FILE = Path("quotes.json")
FAVORITES_FILE = Path("favorites.json")

# Default motivational quotes
DEFAULT_QUOTES = [
    "Believe in yourself and you will be unstoppable.",
    "Do something today that your future self will thank you for.",
    "Small steps every day lead to big results.",
    "Success does not come from comfort zones.",
    "Dream big, work hard, stay focused.",
    "Your only limit is your mind.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from easy work.",
    "Stay positive, work hard, make it happen.",
    "Every day is a new chance to improve yourself."
]

# Quotes by mood
MOOD_QUOTES = {
    "happy": [
        "Keep smiling and share your positive energy with the world.",
        "Happiness grows when you appreciate small things.",
        "Your good mood can inspire others today."
    ],
    "sad": [
        "Bad days are temporary. Keep going.",
        "It is okay to feel sad, but do not give up.",
        "Every difficult moment can make you stronger."
    ],
    "tired": [
        "Rest is also part of progress.",
        "You do not have to do everything today. Take one small step.",
        "Even slow progress is still progress."
    ],
    "stressed": [
        "Take a deep breath. You are doing better than you think.",
        "Focus on one thing at a time.",
        "Stress is temporary, but your strength is real."
    ]
}


def load_json(file_path):
    """
    Loads data from a JSON file.
    If the file does not exist, returns an empty dictionary.
    """
    if not file_path.exists():
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_json(file_path, data):
    """
    Saves data to a JSON file.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to /start command.
    """
    text = (
        "Hello! 👋\n\n"
        "I am your Motivational Quotes Bot.\n"
        "I can send motivational quotes, mood-based quotes, "
        "and save your favorite quotes.\n\n"
        "Available commands:\n"
        "/quote - get a random motivational quote\n"
        "/mood happy - get a quote for your mood\n"
        "/mood sad - get a quote for sadness\n"
        "/mood tired - get a quote when you are tired\n"
        "/mood stressed - get a quote for stress\n"
        "/favorite - save the last quote to favorites\n"
        "/favorites - show saved favorite quotes\n"
        "/add your quote - add your own quote\n"
        "/myquotes - show your own quotes\n"
        "/help - show help menu\n"
        "/about - about this project"
    )

    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to /help command.
    """
    text = (
        "Help Menu 📌\n\n"
        "/start - start the bot\n"
        "/quote - get a random motivational quote\n"
        "/mood happy - quote for happy mood\n"
        "/mood sad - quote for sad mood\n"
        "/mood tired - quote for tired mood\n"
        "/mood stressed - quote for stress\n"
        "/favorite - save the last quote\n"
        "/favorites - show favorite quotes\n"
        "/add your quote - save your own quote\n"
        "/myquotes - show your own saved quotes\n"
        "/about - project description\n\n"
        "Examples:\n"
        "/mood sad\n"
        "/add Never give up!"
    )

    await update.message.reply_text(text)


async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a random quote.
    It uses default quotes and user's own saved quotes.
    """
    data = load_json(QUOTES_FILE)

    user_id = str(update.effective_user.id)
    user_quotes = data.get(user_id, [])

    all_quotes = DEFAULT_QUOTES + user_quotes
    random_quote = random.choice(all_quotes)

    # Save last quote in temporary user data
    context.user_data["last_quote"] = random_quote

    await update.message.reply_text(f"✨ {random_quote}")


async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a quote based on user's mood.
    """
    if not context.args:
        await update.message.reply_text(
            "Please write your mood after /mood.\n\n"
            "Available moods:\n"
            "happy, sad, tired, stressed\n\n"
            "Example:\n"
            "/mood sad"
        )
        return

    user_mood = context.args[0].lower()

    if user_mood not in MOOD_QUOTES:
        await update.message.reply_text(
            "I do not know this mood.\n\n"
            "Available moods:\n"
            "happy, sad, tired, stressed\n\n"
            "Example:\n"
            "/mood tired"
        )
        return

    selected_quote = random.choice(MOOD_QUOTES[user_mood])

    # Save last quote so user can add it to favorites
    context.user_data["last_quote"] = selected_quote

    await update.message.reply_text(f"💭 Mood: {user_mood}\n\n✨ {selected_quote}")


async def favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Saves the last sent quote to user's favorites.
    """
    user_id = str(update.effective_user.id)

    last_quote = context.user_data.get("last_quote")

    if not last_quote:
        await update.message.reply_text(
            "You do not have a quote to save yet.\n\n"
            "First use /quote or /mood, then use /favorite."
        )
        return

    favorites_data = load_json(FAVORITES_FILE)

    if user_id not in favorites_data:
        favorites_data[user_id] = []

    if last_quote in favorites_data[user_id]:
        await update.message.reply_text("This quote is already in your favorites ⭐")
        return

    favorites_data[user_id].append(last_quote)
    save_json(FAVORITES_FILE, favorites_data)

    await update.message.reply_text("Quote saved to favorites ⭐")


async def favorites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows user's favorite quotes.
    """
    user_id = str(update.effective_user.id)
    favorites_data = load_json(FAVORITES_FILE)

    user_favorites = favorites_data.get(user_id, [])

    if not user_favorites:
        await update.message.reply_text(
            "You do not have favorite quotes yet.\n\n"
            "Use /quote or /mood first, then use /favorite."
        )
        return

    text = "Your favorite quotes ⭐\n\n"

    for number, saved_quote in enumerate(user_favorites, start=1):
        text += f"{number}. {saved_quote}\n"

    await update.message.reply_text(text)


async def add_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Saves user's custom quote.
    """
    if not context.args:
        await update.message.reply_text(
            "Please write a quote after /add.\n\n"
            "Example:\n"
            "/add Work hard and believe in yourself."
        )
        return

    quote_text = " ".join(context.args)

    data = load_json(QUOTES_FILE)
    user_id = str(update.effective_user.id)

    if user_id not in data:
        data[user_id] = []

    data[user_id].append(quote_text)
    save_json(QUOTES_FILE, data)

    await update.message.reply_text("Your quote was saved successfully ✅")


async def my_quotes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows user's own added quotes.
    """
    data = load_json(QUOTES_FILE)
    user_id = str(update.effective_user.id)

    user_quotes = data.get(user_id, [])

    if not user_quotes:
        await update.message.reply_text(
            "You have not saved any personal quotes yet.\n\n"
            "Use this command:\n"
            "/add Your motivational quote"
        )
        return

    text = "Your personal quotes 📚\n\n"

    for number, saved_quote in enumerate(user_quotes, start=1):
        text += f"{number}. {saved_quote}\n"

    await update.message.reply_text(text)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Describes the project.
    """
    text = (
        "Project: Motivational Quotes Bot\n\n"
        "This Telegram bot was created using Python and the "
        "python-telegram-bot library.\n\n"
        "Main features:\n"
        "- Sends random motivational quotes\n"
        "- Sends mood-based quotes\n"
        "- Allows users to save favorite quotes\n"
        "- Allows users to add their own quotes\n"
        "- Saves user data in JSON files\n"
        "- Responds to commands and text messages"
    )

    await update.message.reply_text(text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles normal text messages.
    """
    user_text = update.message.text.lower()

    if "quote" in user_text or "motivation" in user_text or "цитата" in user_text:
        await quote(update, context)
    elif "sad" in user_text:
        context.args = ["sad"]
        await mood(update, context)
    elif "happy" in user_text:
        context.args = ["happy"]
        await mood(update, context)
    elif "tired" in user_text:
        context.args = ["tired"]
        await mood(update, context)
    elif "stressed" in user_text:
        context.args = ["stressed"]
        await mood(update, context)
    else:
        await update.message.reply_text(
            "I did not understand that message.\n"
            "Use /help to see available commands."
        )


def main():
    """
    Main function that starts the bot.
    """
    load_dotenv()

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN is missing. Please add it to your .env file.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("mood", mood))
    app.add_handler(CommandHandler("favorite", favorite))
    app.add_handler(CommandHandler("favorites", favorites))
    app.add_handler(CommandHandler("add", add_quote))
    app.add_handler(CommandHandler("myquotes", my_quotes))
    app.add_handler(CommandHandler("about", about))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()