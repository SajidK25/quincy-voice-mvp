import traceback
from redis import Redis
from rq import Worker, Queue, Connection

from api.settings import settings
from api.storage import job_paths, write_text
from api.audio import normalize_to_wav, mix_vocals_over_inst
from api.runpod_client import runpod_convert_full

def _set_status(paths, s: str):
    write_text(paths["status"], s)

def _set_error(paths, e: str):
    write_text(paths["error"], e)

def process_job(job_id: str, raw_upload_path: str):
    paths = job_paths(settings.STORAGE_DIR, job_id)

    try:
        _set_status(paths, "normalizing")
        normalize_to_wav(raw_upload_path, paths["input"])

        _set_status(paths, "runpod_processing")
        # RunPod returns inst + converted vocals
        runpod_convert_full(paths["input"], paths["inst"], paths["converted"])

        _set_status(paths, "merging")
        mix_vocals_over_inst(paths["inst"], paths["converted"], paths["output"])

        _set_status(paths, "ready")

    except Exception as ex:
        _set_status(paths, "failed")
        _set_error(paths, f"{ex}\n\n{traceback.format_exc()}")

def main():
    redis_conn = Redis.from_url(settings.REDIS_URL)
    with Connection(redis_conn):
        worker = Worker([Queue("quincy")])
        worker.work()

if __name__ == "__main__":
    main()
