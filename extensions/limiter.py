from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter = Limiter(
   key_func=get_remote_address,
   default_limits=["100 per minute"],
   storage_uri="redis://host.docker.internal:6379/3"
)
