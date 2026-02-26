import base64
import requests
from api.settings import settings

def _file_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def _b64_to_file(b64_str: str, out_path: str):
    data = base64.b64decode(b64_str)
    with open(out_path, "wb") as f:
        f.write(data)

def runpod_convert_full(input_wav_path: str, inst_out: str, converted_vocal_out: str):
    """Calls RunPod Serverless endpoint that:
    1) splits stems
    2) converts vocals to VOICE_MODEL_ID
    Returns inst.wav + converted vocal wav.
    """
    base_url = settings.RUNPOD_API_URL.rstrip("/")
    # RunPod convention is POST {base}/run, then poll {base}/status/{id}
    run_url = f"{base_url}/run"

    headers = {}
    if settings.RUNPOD_API_KEY:
        headers["Authorization"] = f"Bearer {settings.RUNPOD_API_KEY}"

    payload = {
        "input": {
            "audio_b64": _file_to_b64(input_wav_path),
            "model_id": settings.VOICE_MODEL_ID,
            "return_format": "wav"
        }
    }

    r = requests.post(run_url, json=payload, headers=headers, timeout=600)
    r.raise_for_status()
    j = r.json()

    # Two common patterns:
    # A) sync: {"output": {...}} or {"output": {"inst_wav_b64":..., "converted_vocal_wav_b64":...}}
    # B) async: {"id":"..."} then poll /status/{id} until status == COMPLETED and output present
    if "output" in j:
        out = j["output"]
        # sometimes nested: {"output":{"output":{...}}}
        if isinstance(out, dict) and "output" in out and ("inst_wav_b64" in out["output"] or "converted_vocal_wav_b64" in out["output"]):
            out = out["output"]
        _b64_to_file(out["inst_wav_b64"], inst_out)
        _b64_to_file(out["converted_vocal_wav_b64"], converted_vocal_out)
        return

    if "id" not in j:
        raise RuntimeError("RunPod response missing 'output' and missing async 'id'.")

    job_id = j["id"]
    status_url = f"{base_url}/status/{job_id}"

    # Poll until completed (simple loop; worker is background anyway)
    while True:
        s = requests.get(status_url, headers=headers, timeout=60)
        s.raise_for_status()
        sj = s.json()

        status = (sj.get("status") or sj.get("state") or "").upper()
        if status in ("COMPLETED", "SUCCEEDED"):
            out = sj.get("output") or sj.get("result") or {}
            if isinstance(out, dict) and "output" in out and isinstance(out["output"], dict):
                out = out["output"]
            _b64_to_file(out["inst_wav_b64"], inst_out)
            _b64_to_file(out["converted_vocal_wav_b64"], converted_vocal_out)
            return
        if status in ("FAILED", "CANCELED", "CANCELLED", "ERROR"):
            raise RuntimeError(f"RunPod job failed: {sj}")
