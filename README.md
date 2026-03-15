# django_promocode

REST API для создания заказов с применением промокодов (процентная скидка).

## Стек

- Python 3.12, Django 5, Django REST Framework
- PostgreSQL (prod) / SQLite (dev)
- pytest, factory_boy, ruff, mypy
- Docker, docker-compose

## Quick Start — локально

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Промокоды создаются через Django Admin: http://localhost:8000/admin/

## Quick Start — Docker

```bash
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py createsuperuser
```

## API

### `POST /api/v1/orders/`

**Без промокода:**
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": "1000.00"}'
```
```json
{
    "id": 1,
    "user_id": 1,
    "original_amount": "1000.00",
    "discount_amount": "0.00",
    "final_amount": "1000.00",
    "promo_code": null,
    "created_at": "2025-03-15T12:00:00Z"
}
```

**С промокодом (скидка 15%):**
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "amount": "1000.00", "promo_code": "SUMMER2025"}'
```
```json
{
    "id": 2,
    "user_id": 1,
    "original_amount": "1000.00",
    "discount_amount": "150.00",
    "final_amount": "850.00",
    "promo_code": "SUMMER2025",
    "created_at": "2025-03-15T12:00:00Z"
}
```

**Ошибки промокода** — `400 Bad Request`:
```json
{"error": {"code": "PROMO-001", "message": "Promo code not found"}}
```

| Code | Message |
|------|---------|
| PROMO-001 | Promo code not found |
| PROMO-002 | Promo code has expired |
| PROMO-003 | Promo code usage limit exceeded |
| PROMO-004 | Promo code already used by this user |
| PROMO-005 | Promo code is deactivated |

Несуществующий `user_id` — `404`. Невалидный ввод — `400` (DRF формат).

## Тесты

```bash
pytest
```

## Линтинг

```bash
ruff check . && ruff format --check . && mypy .
```

## Структура проекта

```
├── config/          # Settings (base/dev/prod), urls, wsgi/asgi
├── apps/
│   ├── common/      # TimeStampedModel, PromoCodeError exceptions
│   ├── users/       # Встроенный User (без кастомизации)
│   ├── orders/      # Order model, CreateOrderService, API endpoint
│   └── promocodes/  # PromoCode, PromoCodeUsage models, Admin
├── tests/           # conftest.py, factories.py
├── requirements/    # base.txt, dev.txt
├── Dockerfile
└── docker-compose.yml
```
