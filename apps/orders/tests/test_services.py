"""Unit tests for CreateOrderService."""

from datetime import timedelta
from decimal import Decimal

import pytest
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
from apps.orders.services import CreateOrderService
from apps.promocodes.models import PromoCodeUsage
from tests.factories import OrderFactory, PromoCodeFactory, PromoCodeUsageFactory, UserFactory


@pytest.mark.django_db
class TestCreateOrderService:
    """Tests for order creation with and without promo codes."""

    def test_create_order_without_promo(self) -> None:
        user = UserFactory()
        amount = Decimal("1000.00")

        order = CreateOrderService.execute(user_id=user.id, amount=amount)

        assert order.original_amount == amount
        assert order.discount_amount == Decimal("0.00")
        assert order.final_amount == amount
        assert order.promo_code is None

    def test_create_order_with_valid_promo(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(discount_percent=Decimal("15.00"))
        amount = Decimal("1000.00")

        order = CreateOrderService.execute(user_id=user.id, amount=amount, promo_code=promo.code)

        assert order.discount_amount == Decimal("150.00")
        assert order.final_amount == Decimal("850.00")
        assert order.promo_code == promo

    def test_promo_not_found_raises_error(self) -> None:
        user = UserFactory()

        with pytest.raises(PromoCodeNotFound) as exc_info:
            CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code="NONEXISTENT")
        assert exc_info.value.code == "PROMO-001"

    def test_promo_expired_raises_error(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(
            valid_from=timezone.now() - timedelta(days=10),
            valid_until=timezone.now() - timedelta(days=1),
        )

        with pytest.raises(PromoCodeExpired) as exc_info:
            CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)
        assert exc_info.value.code == "PROMO-002"

    def test_promo_usage_limit_exceeded(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(max_usages=1, current_usages=1)

        with pytest.raises(PromoCodeUsageLimitExceeded) as exc_info:
            CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)
        assert exc_info.value.code == "PROMO-003"

    def test_promo_already_used_by_user(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory()
        order = OrderFactory(user=user)
        PromoCodeUsageFactory(user=user, promo_code=promo, order=order)

        with pytest.raises(PromoCodeAlreadyUsedByUser) as exc_info:
            CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)
        assert exc_info.value.code == "PROMO-004"

    def test_promo_deactivated_raises_error(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(is_active=False)

        with pytest.raises(PromoCodeDeactivated) as exc_info:
            CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)
        assert exc_info.value.code == "PROMO-005"

    def test_promo_usages_incremented(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(current_usages=5)

        CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)

        promo.refresh_from_db()
        assert promo.current_usages == 6

    def test_promo_usage_record_created(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory()

        CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)

        assert PromoCodeUsage.objects.filter(user=user, promo_code=promo).exists()

    def test_promo_code_case_insensitive(self) -> None:
        user = UserFactory()
        PromoCodeFactory(code="SUMMER2025")

        order = CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code="summer2025")

        assert order.promo_code is not None
        assert order.promo_code.code == "SUMMER2025"

    def test_discount_calculation_rounding(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(discount_percent=Decimal("33.33"))

        order = CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)

        assert order.discount_amount == Decimal("33.33")
        assert order.final_amount == Decimal("66.67")

    def test_user_not_found_raises_404(self) -> None:
        with pytest.raises(Http404):
            CreateOrderService.execute(user_id=99999, amount=Decimal("100.00"))

    def test_order_not_created_on_promo_error(self) -> None:
        user = UserFactory()
        promo = PromoCodeFactory(is_active=False)
        initial_count = Order.objects.count()

        with pytest.raises(PromoCodeDeactivated):
            CreateOrderService.execute(user_id=user.id, amount=Decimal("100.00"), promo_code=promo.code)

        assert Order.objects.count() == initial_count
