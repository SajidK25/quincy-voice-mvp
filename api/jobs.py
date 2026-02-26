from redis import Redis
from rq import Queue
from api.settings import settings

def get_queue():
    redis_conn = Redis.from_url(settings.REDIS_URL)
    return Queue("quincy", connection=redis_conn)
