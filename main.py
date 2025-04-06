from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
from tempfile import NamedTemporaryFile
import whisper
from PIL import Image
import face_recognition
import subprocess

app = FastAPI()

# Load Whisper model once
whisper_model = whisper.load_model("base")

@app.get("/")
def home():
    return {"status": "ClipFinder AI backend is running."}

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    # Save uploaded file
    try:
        with NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    try:
        audio_path = tmp_path.replace(".mp4", ".wav")
        frames_dir = "frames_output"
        os.makedirs(frames_dir, exist_ok=True)

        # Extract audio using ffmpeg
        subprocess.run(["ffmpeg", "-i", tmp_path, "-q:a", "0", "-map", "a", audio_path], check=True)

        # Extract frames from video
        subprocess.run(["ffmpeg", "-i", tmp_path, f"{frames_dir}/frame_%03d.jpg"], check=True)

        # Transcribe audio
        result = whisper_model.transcribe(audio_path)
        transcription = result.get("text", "")

        # Analyze faces in first 10 frames
        detected_faces = []
        for i in range(1, 11):
            frame_path = os.path.join(frames_dir, f"frame_{i:03d}.jpg")
            if not os.path.exists(frame_path):
                continue
            image = face_recognition.load_image_file(frame_path)
            face_locations = face_recognition.face_locations(image)
            if face_locations:
                detected_faces.append({"frame": i, "faces": len(face_locations)})

        return {
            "transcription": transcription,
            "face_frames": detected_faces
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        # Clean up temporary files
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        shutil.rmtree(frames_dir, ignore_errors=True)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
