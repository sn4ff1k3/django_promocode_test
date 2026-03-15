from config.settings.base import *  # noqa: F401, F403

SECRET_KEY = "django-insecure-dev-key-change-in-production"

DEBUG = True

ALLOWED_HOSTS: list[str] = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}
