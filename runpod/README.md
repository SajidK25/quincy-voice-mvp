# RunPod Serverless Handler (Skeleton)

This folder is a developer handoff skeleton. Your dev will:
- Pick a stem splitter (Demucs is common)
- Pick a voice conversion engine (RVC is common)
- Ensure output returns:
  - inst_wav_b64
  - converted_vocal_wav_b64

## Expected request (from Render worker)
POST {RUNPOD_API_URL}/run
{
  "input": {
    "audio_b64": "<base64 of wav>",
    "model_id": "<VOICE_MODEL_ID>",
    "return_format": "wav"
  }
}

## Expected response (sync or async)
Sync:
{ "output": { "inst_wav_b64": "...", "converted_vocal_wav_b64": "..." } }

Async:
{ "id": "..." } then GET {RUNPOD_API_URL}/status/{id} -> { "status":"COMPLETED", "output": {...} }
