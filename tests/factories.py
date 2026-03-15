"""Factory Boy factories for creating test data."""

from datetime import timedelta
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.orders.models import Order
from apps.promocodes.models import PromoCode, PromoCodeUsage

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Creates a User instance with sequential username."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")


class PromoCodeFactory(factory.django.DjangoModelFactory):
    """Creates a valid PromoCode with sensible defaults."""

    class Meta:
        model = PromoCode

    code = factory.Sequence(lambda n: f"PROMO{n:04d}")
    discount_percent = Decimal("15.00")
    max_usages = 100
    current_usages = 0
    valid_from = factory.LazyFunction(lambda: timezone.now() - timedelta(days=1))
    valid_until = factory.LazyFunction(lambda: timezone.now() + timedelta(days=1))
    is_active = True


class OrderFactory(factory.django.DjangoModelFactory):
    """Creates an Order without promo code discount."""

    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    original_amount = Decimal("1000.00")
    discount_amount = Decimal("0.00")
    final_amount = Decimal("1000.00")


class PromoCodeUsageFactory(factory.django.DjangoModelFactory):
    """Creates a PromoCodeUsage linking user, promo code, and order."""

    class Meta:
        model = PromoCodeUsage

    user = factory.SubFactory(UserFactory)
    promo_code = factory.SubFactory(PromoCodeFactory)
    order = factory.SubFactory(OrderFactory)
