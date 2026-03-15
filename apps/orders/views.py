"""API view for order creation endpoint."""

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.exceptions import PromoCodeError
from apps.orders.serializers import CreateOrderSerializer, OrderResponseSerializer
from apps.orders.services import CreateOrderService


class CreateOrderView(APIView):
    """Handle POST /api/v1/orders/ to create an order."""

    def post(self, request: Request) -> Response:
        """Validate input, delegate to service, return order or error."""
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            order = CreateOrderService.execute(**serializer.validated_data)
        except PromoCodeError as e:
            return Response(
                {"error": {"code": e.code, "message": e.message}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            OrderResponseSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )
