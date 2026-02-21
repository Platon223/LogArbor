from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(
   key_func=get_remote_address,
   default_limits=["100 per minute"],
   storage_uri="redis://127.0.0.1:6379/3"
)
