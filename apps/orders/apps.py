"""Orders app: Order model, CreateOrderService, and API endpoint."""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the orders app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orders"
