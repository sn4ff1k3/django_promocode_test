"""Django Admin configuration for the PromoCode model."""

from django.contrib import admin

from apps.promocodes.models import PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    """Admin view for promo codes with filtering and search."""

    list_display = (
        "code",
        "discount_percent",
        "max_usages",
        "current_usages",
        "valid_from",
        "valid_until",
        "is_active",
    )
    list_filter = ("is_active", "valid_from")
    search_fields = ("code",)
    readonly_fields = ("current_usages", "created_at", "updated_at")
