import os

import dj_database_url

from config.settings.base import *  # noqa: F401, F403

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

DATABASES = {"default": dj_database_url.config(default=os.environ.get("DATABASE_URL"))}
