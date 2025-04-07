import os
import tempfile
import logging
import cv2
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from deepface import DeepFace
import whisper
from transformers import CLIPProcessor, CLIPModel
import torch
import numpy as np

# === Configuration ===
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set in your Render environment or .env file

# === Logging setup ===
logging.basicConfig(level=logging.INFO)
app = ApplicationBuilder().token(TOKEN).build()

# === Load Models ===
logging.info("Loading models...")
whisper_model = whisper.load_model("base")
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
logging.info("Models loaded.")

# === Helper Function: Extract Frames ===
def extract_frames(video_path, interval=1):
    frames = []
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if int(frame_count % (fps * interval)) == 0:
            frames.append(frame)
        frame_count += 1
    cap.release()
    return frames

# === Helper Function: Detect Faces using DeepFace ===
def detect_faces(frames):
    detected_faces = []
    for frame in frames:
        try:
            results = DeepFace.extract_faces(img_path=frame, enforce_detection=False)
            detected_faces.extend(results)
        except Exception as e:
            logging.warning(f"Face detection error: {e}")
            continue
    return detected_faces

# === Helper Function: Transcribe Audio using Whisper ===
def transcribe_audio(video_path):
    try:
        result = whisper_model.transcribe(video_path)
        return result.get("text", "")
    except Exception as e:
        logging.warning(f"Whisper error: {e}")
        return ""

# === Helper Function: Get CLIP Embedding for an Image ===
def get_clip_embedding(image):
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = clip_model.get_image_features(**inputs)
    return outputs.cpu().numpy()

# === Telegram Handler for Video ===
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video = update.message.video or update.message.document
    file = await context.bot.get_file(video.file_id)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tf:
        await file.download_to_drive(tf.name)
        video_path = tf.name

    await update.message.reply_text("Analyzing video...")

    # Step 1: Extract frames
    frames = extract_frames(video_path, interval=1)
    await update.message.reply_text(f"Extracted {len(frames)} key frames.")

    # Step 2: Detect faces
    faces = detect_faces(frames)
    await update.message.reply_text(f"Detected {len(faces)} faces in video.")

    # Step 3: Transcribe audio
    transcript = transcribe_audio(video_path)
    await update.message.reply_text(f"Transcript:\n{transcript[:1000]}...")

    # Step 4: CLIP embedding for first frame (placeholder for matching)
    if frames:
        clip_vec = get_clip_embedding(frames[0])
        await update.message.reply_text("Visual features extracted (CLIP vector ready).")

    # Future steps: FAISS matching, actor/show identification
    await update.message.reply_text("Source identification module coming soon.")

# === Attach Handler ===
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))

# === Start Bot ===
if __name__ == "__main__":
    app.run_polling()
