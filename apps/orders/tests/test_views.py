from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from tests.factories import PromoCodeFactory, UserFactory


@pytest.mark.django_db
class TestCreateOrderView:
    url = "/api/v1/orders/"

    def test_create_order_returns_201(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()

        # Act
        response = api_client.post(self.url, {"user_id": user.id, "amount": "1000.00"}, format="json")

        # Assert
        assert response.status_code == 201

    def test_create_order_with_promo_returns_201(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()
        promo = PromoCodeFactory(discount_percent=Decimal("15.00"))

        # Act
        response = api_client.post(
            self.url,
            {"user_id": user.id, "amount": "1000.00", "promo_code": promo.code},
            format="json",
        )

        # Assert
        assert response.status_code == 201
        assert Decimal(response.data["discount_amount"]) > 0
        assert response.data["promo_code"] == promo.code

    def test_invalid_promo_returns_400(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()

        # Act
        response = api_client.post(
            self.url,
            {"user_id": user.id, "amount": "100.00", "promo_code": "INVALID"},
            format="json",
        )

        # Assert
        assert response.status_code == 400
        assert response.data["error"]["code"] == "PROMO-001"

    def test_missing_amount_returns_400(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()

        # Act
        response = api_client.post(self.url, {"user_id": user.id}, format="json")

        # Assert
        assert response.status_code == 400
        assert "amount" in response.data

    def test_negative_amount_returns_400(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()

        # Act
        response = api_client.post(
            self.url,
            {"user_id": user.id, "amount": "-10.00"},
            format="json",
        )

        # Assert
        assert response.status_code == 400

    def test_user_not_found_returns_404(self, api_client: APIClient) -> None:
        # Arrange & Act
        response = api_client.post(self.url, {"user_id": 99999, "amount": "100.00"}, format="json")

        # Assert
        assert response.status_code == 404

    def test_response_format_matches_contract(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()

        # Act
        response = api_client.post(self.url, {"user_id": user.id, "amount": "1000.00"}, format="json")

        # Assert
        expected_keys = {
            "id",
            "user_id",
            "original_amount",
            "discount_amount",
            "final_amount",
            "promo_code",
            "created_at",
        }
        assert set(response.data.keys()) == expected_keys

    def test_empty_promo_code_treated_as_none(self, api_client: APIClient) -> None:
        # Arrange
        user = UserFactory()

        # Act
        response = api_client.post(
            self.url,
            {"user_id": user.id, "amount": "1000.00", "promo_code": ""},
            format="json",
        )

        # Assert
        assert response.status_code == 201
        assert response.data["promo_code"] is None
        assert response.data["discount_amount"] == "0.00"
