import os
import uuid
from pathlib import Path

def ensure_dir(p: str):
    Path(p).mkdir(parents=True, exist_ok=True)

def new_job_id() -> str:
    return uuid.uuid4().hex

def job_dir(storage_dir: str, job_id: str) -> str:
    return os.path.join(storage_dir, "jobs", job_id)

def job_paths(storage_dir: str, job_id: str):
    d = job_dir(storage_dir, job_id)
    ensure_dir(d)
    return {
        "dir": d,
        "input": os.path.join(d, "input.wav"),
        "inst": os.path.join(d, "inst.wav"),
        "converted": os.path.join(d, "converted.wav"),
        "output": os.path.join(d, "output.wav"),
        "status": os.path.join(d, "status.txt"),
        "error": os.path.join(d, "error.txt"),
    }

def write_text(path: str, txt: str):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)

def read_text(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def file_exists(path: str):
    return os.path.exists(path) and os.path.getsize(path) > 0
