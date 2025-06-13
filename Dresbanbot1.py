import os
import random
from string import ascii_letters, digits
from typing import Dict, List

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.error import Forbidden

# Replace with your own bot token
BOT_TOKEN = 'replace bot token here'

# Define states for the conversation
WAITING_FOR_CHANNEL_LINK = range(1)

async def start(update: Update, context):
    await update.message.reply_text('Please enter the channel link you want to terminate (e.g., @channelusername):')
    return WAITING_FOR_CHANNEL_LINK

async def send_reports(update: Update, context):
    channel_link = update.message.text.strip()

    # Validate the channel link format (basic validation)
    if not channel_link.startswith('@'):
        await update.message.reply_text('Invalid channel link. Please enter a valid link starting with @.')
        return WAITING_FOR_CHANNEL_LINK

    messages = generate_fake_messages(5)  # Generate 5 fake messages
    media = generate_fake_media(2)  # Generate 2 fake media files

    bot = context.bot
    try:
        for message in messages:
            await bot.send_message(channel_link, message)
        await bot.send_media_group(channel_link, media)
        await update.message.reply_text('Reports sent successfully!')
    except Forbidden:
        # If the bot is not a member of the channel, attempt to join it first
        try:
            await bot.join_chat(channel_link)
        except Forbidden:
            await update.message.reply_text('Error: The bot was unable to join the channel. Make sure the bot has the necessary permissions.')
            return WAITING_FOR_CHANNEL_LINK
        else:
            # Send the reports again after joining the channel
            for message in messages:
                await bot.send_message(channel_link, message)
            await bot.send_media_group(channel_link, media)
            await update.message.reply_text('Reports sent successfully!')

    return ConversationHandler.END

def generate_fake_messages(num_messages: int) -> List[str]:
    messages = []
    for _ in range(num_messages):
        messages.append(''.join(random.choice(ascii_letters + digits) for _ in range(200)))
    return messages

def generate_fake_media(num_media: int) -> List[bytes]:
    media = []
    for _ in range(num_media):
        media.append(b''.join(random.choice(ascii_letters + digits).encode() for _ in range(1024 * 1024)))
    return media

async def cancel(update: Update, context):
    await update.message.reply_text('Operation cancelled.')
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Define the conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAITING_FOR_CHANNEL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_reports)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()
    print("Bot is running. Enter /stop to stop the script.")

if __name__ == '__main__':
    main()

#codedbyzlodontbeskidclaimingitasyours
