from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

redis_storage_limiter = os.getenv("REDIS_STORAGE_LIMITER", "redis://127.0.0.1:6379/2")

limiter = Limiter(
   key_func=get_remote_address,
   default_limits=["100 per minute"],
   storage_uri=redis_storage_limiter
)
