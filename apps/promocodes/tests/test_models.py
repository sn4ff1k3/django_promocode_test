"""Model tests for PromoCode and PromoCodeUsage."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.promocodes.models import PromoCode, PromoCodeUsage
from tests.factories import OrderFactory, PromoCodeFactory, UserFactory


@pytest.mark.django_db
class TestPromoCodeModel:
    """Tests for PromoCode __str__, save normalization, and constraints."""

    def test_promo_code_str_returns_code(self) -> None:
        promo = PromoCodeFactory(code="SUMMER")

        assert str(promo) == "SUMMER"

    def test_promo_code_saved_uppercase(self) -> None:
        promo = PromoCodeFactory(code="summer")

        promo.refresh_from_db()
        assert promo.code == "SUMMER"

    def test_unique_constraint_user_promo(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory()
        order1 = OrderFactory(user=user)
        PromoCodeUsage.objects.create(user=user, promo_code=promo, order=order1)
        order2 = OrderFactory(user=user)

        with pytest.raises(IntegrityError):
            PromoCodeUsage.objects.create(user=user, promo_code=promo, order=order2)

    def test_valid_until_before_valid_from_constraint(self) -> None:
        now = timezone.now()

        with pytest.raises(IntegrityError):
            PromoCode.objects.create(
                code="BADDATE",
                discount_percent="10.00",
                max_usages=10,
                valid_from=now + timedelta(days=5),
                valid_until=now - timedelta(days=5),
            )
