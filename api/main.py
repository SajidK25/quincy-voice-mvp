import os
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from api.settings import settings
from api.storage import new_job_id, job_paths, write_text, read_text, file_exists
from api.jobs import get_queue

app = FastAPI(title="Quincy Voice MVP (RunPod)")

def auth(x_api_key: str | None):
    if not x_api_key or x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/jobs")
async def create_job(file: UploadFile = File(...), x_api_key: str | None = Header(default=None)):
    auth(x_api_key)

    job_id = new_job_id()
    paths = job_paths(settings.STORAGE_DIR, job_id)

    raw_path = os.path.join(paths["dir"], f"upload_{file.filename}")
    with open(raw_path, "wb") as f:
        f.write(await file.read())

    write_text(paths["status"], "queued")
    q = get_queue()
    q.enqueue("worker.worker.process_job", job_id, raw_path)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_status(job_id: str, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    paths = job_paths(settings.STORAGE_DIR, job_id)
    status = read_text(paths["status"]) or "unknown"
    err = read_text(paths["error"])
    return {"job_id": job_id, "status": status, "error": err}

@app.get("/jobs/{job_id}/download")
def download(job_id: str, x_api_key: str | None = Header(default=None)):
    auth(x_api_key)
    paths = job_paths(settings.STORAGE_DIR, job_id)

    if not file_exists(paths["output"]):
        status = read_text(paths["status"]) or "unknown"
        err = read_text(paths["error"])
        return JSONResponse(status_code=404, content={"detail":"Output not ready","status":status,"error":err})

    return FileResponse(paths["output"], media_type="audio/wav", filename=f"quincy_{job_id}.wav")
