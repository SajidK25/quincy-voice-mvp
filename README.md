# Quincy Voice Converter (Render + RunPod)

Goal:
Upload a Suno song and automatically get back the same track with vocals converted to Quincy voice.

## What runs where
- Render (CPU): Web UI + FastAPI + background worker + Redis + ffmpeg merge
- RunPod (GPU): One serverless endpoint does stem split + voice conversion and returns:
  - inst_wav_b64
  - converted_vocal_wav_b64

## Render Environment Variables
API + Worker:
- API_KEY (MVP shared secret)
- REDIS_URL (Render managed)
- STORAGE_DIR=/var/data
- RUNPOD_API_URL (example: https://api.runpod.ai/v2/<endpoint_id>)
- RUNPOD_API_KEY (optional bearer token)
- VOICE_MODEL_ID (your Quincy model id used by RunPod handler)

Web:
- VITE_API_BASE_URL=https://<quincy-api>.onrender.com
- VITE_API_KEY=<same as API_KEY>  (MVP only; not secure for public)

## API
POST /jobs (multipart file) -> {job_id}
GET  /jobs/{job_id} -> status
GET  /jobs/{job_id}/download -> wav

## Notes
- This MVP returns WAV. Your dev can add MP3 export easily with ffmpeg.
- The only part your dev must implement/host is the RunPod GPU handler.
