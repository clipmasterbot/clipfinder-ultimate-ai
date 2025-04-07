# Clip Finder Bot - Minimal Version

This Telegram bot automatically analyzes uploaded video clips to:
- Extract audio using OpenAI Whisper
- Detect faces from video frames using DeepFace
- Extract image embeddings using CLIP
- Provide intelligent scene insight and actor presence based on video content

## Features
- Accepts video files via Telegram
- Extracts frames from video (1 frame/sec)
- Detects faces from frames
- Runs CLIP to generate visual embeddings
- Transcribes audio using Whisper

## Requirements
Install dependencies with:

```bash
pip install -r requirements.txt
