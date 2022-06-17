"""🇹🇼🧾 Python SDK for accessing Taiwan E-Inovice API"""
from datetime import datetime

from .app_client import AppClient  # noqa

__version__ = datetime.today().strftime("%Y.%m.%d") + "b"  # b represent beta version
