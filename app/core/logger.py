import logging
from core.settings import settings

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(pathname)s: %(message)s"
)
handler.setFormatter(formatter)

logger.addHandler(handler)
