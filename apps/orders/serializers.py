from decimal import Decimal

from rest_framework import serializers

from apps.orders.models import Order


class CreateOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    promo_code = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True, default=None)

    def validate_promo_code(self, value: str | None) -> str | None:
        if value is not None and not value.strip():
            return None
        return value


class OrderResponseSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    promo_code = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user_id", "original_amount", "discount_amount", "final_amount", "promo_code", "created_at"]

    def get_promo_code(self, obj: Order) -> str | None:
        if obj.promo_code:
            return obj.promo_code.code
        return None
