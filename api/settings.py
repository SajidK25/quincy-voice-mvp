from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MVP shared secret (frontend sends this; NOT secure for public apps)
    API_KEY: str = "dev"

    # Render Redis URL
    REDIS_URL: str

    # Render Disk mount path (e.g., /var/data)
    STORAGE_DIR: str = "/tmp/quincy_storage"

    # RunPod Serverless endpoint URL (your deployed endpoint base URL)
    # Example: https://api.runpod.ai/v2/<endpoint_id>
    RUNPOD_API_URL: str

    # RunPod API key (optional if you embed it in the URL or use another auth)
    # Example header: Authorization: Bearer <RUNPOD_API_KEY>
    RUNPOD_API_KEY: str = ""

    # Your saved Quincy voice model identifier used by the RunPod handler
    VOICE_MODEL_ID: str

    # Optional base url for absolute links
    BASE_URL: str = ""

    class Config:
        case_sensitive = False

settings = Settings()
