"""Promocodes app: PromoCode and PromoCodeUsage models."""

from django.apps import AppConfig


class PromocodesConfig(AppConfig):
    """Configuration for the promocodes app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.promocodes"
