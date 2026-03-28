import os

from .base import *  # noqa: F401,F403

DEBUG = os.environ.get("DEBUG", "false").lower() in ("1", "true", "yes")  # noqa: F405

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "true").lower() in (
    "1",
    "true",
    "yes",
)
