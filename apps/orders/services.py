"""Business logic for order creation with promo code validation."""

from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import Http404
from django.utils import timezone

from apps.common.exceptions import (
    PromoCodeAlreadyUsedByUser,
    PromoCodeDeactivated,
    PromoCodeExpired,
    PromoCodeNotFound,
    PromoCodeUsageLimitExceeded,
)
from apps.orders.models import Order
from apps.promocodes.models import PromoCode, PromoCodeUsage

User = get_user_model()


class CreateOrderService:
    """Service for creating orders with optional promo code application."""

    @staticmethod
    def execute(user_id: int, amount: Decimal, promo_code: str | None = None) -> Order:
        """Create an order, applying promo code discount if provided."""
        user = User.objects.filter(pk=user_id).first()
        if user is None:
            raise Http404()

        if promo_code is None:
            return Order.objects.create(
                user=user,
                original_amount=amount,
                discount_amount=Decimal("0.00"),
                final_amount=amount,
                promo_code=None,
            )

        with transaction.atomic():
            promo = PromoCode.objects.select_for_update().filter(code=promo_code.upper()).first()
            if promo is None:
                raise PromoCodeNotFound()

            if not promo.is_active:
                raise PromoCodeDeactivated()

            now = timezone.now()
            if not (promo.valid_from <= now <= promo.valid_until):
                raise PromoCodeExpired()

            if promo.current_usages >= promo.max_usages:
                raise PromoCodeUsageLimitExceeded()

            if PromoCodeUsage.objects.filter(user=user, promo_code=promo).exists():
                raise PromoCodeAlreadyUsedByUser()

            discount = (amount * promo.discount_percent / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            final_amount = amount - discount

            order = Order.objects.create(
                user=user,
                original_amount=amount,
                discount_amount=discount,
                final_amount=final_amount,
                promo_code=promo,
            )

            try:
                PromoCodeUsage.objects.create(user=user, promo_code=promo, order=order)
            except IntegrityError:
                raise PromoCodeAlreadyUsedByUser()

            PromoCode.objects.filter(pk=promo.pk).update(current_usages=F("current_usages") + 1)

        return order
