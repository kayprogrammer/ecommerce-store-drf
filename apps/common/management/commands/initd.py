from django.core.management.base import BaseCommand
from .data_script import CreateData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init() -> None:
    CreateData()


class Command(BaseCommand):
    def handle(self, **options) -> None:
        logger.info("Creating initial data")
        init()
        logger.info("Initial data created")
