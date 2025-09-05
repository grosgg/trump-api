"""Logger for the whole app"""
import logging

from app.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
