"""Root-level pytest fixtures shared across all test modules."""

import pytest
from rest_framework.test import APIClient

from tests.factories import PromoCodeFactory, UserFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_promo():
    return PromoCodeFactory()
