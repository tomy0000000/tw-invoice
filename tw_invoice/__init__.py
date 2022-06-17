"""🇹🇼🧾 Python SDK for accessing Taiwan E-Inovice API"""
import os
from datetime import datetime
from random import randint

from .app_client import AppAPIClient  # noqa

VERSION = datetime.today().strftime("%Y.%-m.%d") + "b"  # b represent beta version

GITHUB_ACTION = os.getenv("GITHUB_ACTION")

if GITHUB_ACTION == "publish-to-test-pypi":
    VERSION = f"{VERSION}{randint(0, 10000)}"

__version__ = VERSION
