"""PromoCode and PromoCodeUsage ORM models."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class PromoCode(TimeStampedModel):
    """Discount promo code with usage limits and validity period."""

    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("100.00"))],
    )
    max_usages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    current_usages = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valid_until__gt=models.F("valid_from")),
                name="valid_until_after_valid_from",
            ),
        ]

    def save(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Normalize code to uppercase before saving."""
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.code


class PromoCodeUsage(models.Model):
    """Records which user used which promo code in which order."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="promo_code_usages",
    )
    promo_code = models.ForeignKey(
        PromoCode,
        on_delete=models.CASCADE,
        related_name="usages",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="promo_code_usage",
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "promo_code")

    def __str__(self) -> str:
        return f"{self.user} — {self.promo_code}"
