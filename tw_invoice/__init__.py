"""🇹🇼🧾 Python SDK for accessing Taiwan E-Inovice API"""
import os
from datetime import datetime
from uuid import uuid4

from .app_client import AppAPIClient  # noqa

VERSION = datetime.today().strftime("%Y.%m.%d") + "b"  # b represent beta version

GITHUB_ACTION = os.getenv("GITHUB_ACTION")
GITHUB_SHA = os.getenv("GITHUB_SHA")
if GITHUB_ACTION == "publish-to-test-pypi":
    VERSION = f"{VERSION}-{GITHUB_SHA}-{str(uuid4())[:8]}"

__version__ = VERSION
