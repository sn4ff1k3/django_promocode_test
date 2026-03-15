"""Django Admin configuration for the Order model."""

from django.contrib import admin

from apps.orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin view for orders with user and promo code details."""

    list_display = ("id", "user", "original_amount", "discount_amount", "final_amount", "promo_code", "created_at")
    list_filter = ("created_at",)
    raw_id_fields = ("user", "promo_code")
