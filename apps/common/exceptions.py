"""Domain exceptions for promo code validation."""


class PromoCodeError(Exception):
    """Base exception for promo code errors."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class PromoCodeNotFound(PromoCodeError):
    """Raised when promo code does not exist in the database."""

    def __init__(self) -> None:
        super().__init__("PROMO-001", "Promo code not found")


class PromoCodeExpired(PromoCodeError):
    """Raised when promo code is outside its valid date range."""

    def __init__(self) -> None:
        super().__init__("PROMO-002", "Promo code has expired")


class PromoCodeUsageLimitExceeded(PromoCodeError):
    """Raised when promo code has reached its maximum usage count."""

    def __init__(self) -> None:
        super().__init__("PROMO-003", "Promo code usage limit exceeded")


class PromoCodeAlreadyUsedByUser(PromoCodeError):
    """Raised when the user has already applied this promo code."""

    def __init__(self) -> None:
        super().__init__("PROMO-004", "Promo code already used by this user")


class PromoCodeDeactivated(PromoCodeError):
    """Raised when promo code has is_active=False."""

    def __init__(self) -> None:
        super().__init__("PROMO-005", "Promo code is deactivated")
