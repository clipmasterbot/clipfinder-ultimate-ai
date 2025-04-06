import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatAction
import logging

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a video clip and I’ll try to identify the actor or show!")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action=ChatAction.UPLOAD_VIDEO)
    video_file = await update.message.video.get_file()
    video_path = f"{video_file.file_id}.mp4"
    await video_file.download_to_drive(video_path)

    await update.message.reply_text("Video received. Starting analysis...")
    # Placeholder: future call to recognition pipeline
    await update.message.reply_text("Processing not yet implemented. Coming next!")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.VIDEO, handle_video))

if __name__ == '__main__':
    app.run_polling()
