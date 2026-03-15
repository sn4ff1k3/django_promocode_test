class PromoCodeError(Exception):
    """Base exception for promo code errors."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class PromoCodeNotFound(PromoCodeError):
    def __init__(self) -> None:
        super().__init__("PROMO-001", "Promo code not found")


class PromoCodeExpired(PromoCodeError):
    def __init__(self) -> None:
        super().__init__("PROMO-002", "Promo code has expired")


class PromoCodeUsageLimitExceeded(PromoCodeError):
    def __init__(self) -> None:
        super().__init__("PROMO-003", "Promo code usage limit exceeded")


class PromoCodeAlreadyUsedByUser(PromoCodeError):
    def __init__(self) -> None:
        super().__init__("PROMO-004", "Promo code already used by this user")


class PromoCodeDeactivated(PromoCodeError):
    def __init__(self) -> None:
        super().__init__("PROMO-005", "Promo code is deactivated")
