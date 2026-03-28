# Restro backend

Django REST API for **one restaurant** on this server: one database, one `RestaurantConfig` row for public profile and non-secret defaults. There is no multi-tenant switching.

**Secrets** (payment keys, aggregator API keys, commission overrides you treat as sensitive) live in **environment variables** and `config/settings/base.py` — not in the database — so they are not returned by the public venue API or stored where ORM serializers could leak them.

## Mental model

| Concept | Meaning |
|--------|---------|
| **Single restaurant** | Menu, tables, orders, and staff all belong to this deployment. |
| **DB vs env** | Editable **venue** data (name, address, tax, currency, contact) in `RestaurantConfig`. **Keys and secrets** only in `.env` / process environment. |
| **Frontend** | Branding (logos, theme) stays in the frontend; the API exposes operational venue fields only. |

## Repository layout

```
restro_backend/
├── manage.py
├── requirements.txt
├── README.md
├── config/                      # Django project (settings, root URLs, WSGI/ASGI)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── accounts/                # Staff users (JWT); roles: manager, captain, kitchen
    ├── venue/                   # Restaurant profile (singleton), tables; ``venue.selectors.get_restaurant_config``
    ├── menu/                    # Categories and menu items
    ├── sessions/                # Dine-in table sessions (QR, captain)
    ├── orders/                  # Orders and line items (dine-in + delivery + web)
    ├── billing/                 # Bills and payments
    ├── analytics/               # Aggregated daily / per-item stats
    └── audit/                   # Append-only audit log
```

Each app follows the same pattern:

- `models.py` — domain data for this bounded context.
- `admin.py` — Django admin registration (minimal).
- `serializers.py` — DRF serializers (**stubs**; wire fields and validation when you implement endpoints).
- `views.py` — DRF views (**stubs**; no business logic yet).
- `urls.py` — URLConf include target under `api/v1/...` (**empty `urlpatterns` until views exist**).

## Domain overview

- **`venue.RestaurantConfig`**: One row: name, legal name, contact, address, `timezone`, `tax_rate`, `currency` (**no secrets**). Payment/aggregator keys stay in env vars (see **Configuration**).
- **`venue.Table`**: Floor tables; `qr_token` / expiry exist in the DB for your app logic but **default API serializers omit them** so guests do not receive QR secrets from generic endpoints. Use `TableStaffSerializer` only on authenticated staff routes.
- **`menu`**: Categories (optional `slug` / `description`) and items with `metadata` JSON for allergens, spice level, POS codes, etc.
- **`sessions.TableSession`**: Links a guest session to a table and optional captain.
- **`orders`**: `Order` / `OrderItem` with channels including dine-in, aggregators, **website**, **takeaway**, and **phone**.
- **`billing`**: `Bill` per closed session flow; `Payment` with gateway/method.
- **`analytics`**: Rollups; optional `channel_metrics` JSON on daily rows for channels you do not model as separate columns.
- **`audit`**: Immutable-style log of mutations (enforcement in services later).

## API surface (planned)

Root URLs mount versioned includes, for example:

- `/api/v1/accounts/`
- `/api/v1/venue/`
- `/api/v1/menu/`
- `/api/v1/sessions/`
- `/api/v1/orders/`
- `/api/v1/billing/`
- `/api/v1/analytics/`
- `/api/v1/audit/`

Stub modules compile; **endpoints are added when you implement views and routes**.

## Configuration

- **Database**: **SQLite** by default (`db.sqlite3` next to `manage.py`). PostgreSQL env vars are documented in `.env` for when you switch `DATABASES` in `config/settings/base.py` (or `production.py`).
- **Auth**: JWT via `djangorestframework-simplejwt` (see `REST_FRAMEWORK` in `config/settings/base.py`).
- **CORS**: Set `CORS_ALLOWED_ORIGINS` (comma-separated). `django-cors-headers` is enabled in base settings.
- **Redis / Celery / Channels**: Broker and channel layer URLs via `REDIS_URL`.
- **Payment / aggregator secrets (environment only)** — read from `django.conf.settings` (`config/settings/base.py`):
  - `SWIGGY_API_KEY`, `ZOMATO_API_KEY`
  - `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`
  - `SWIGGY_COMMISSION_PCT`, `ZOMATO_COMMISSION_PCT` (decimals, defaults `18` and `20` if unset/invalid)

## Running locally

```bash
cd restro_backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

After adding real endpoints, document them in your frontend repo or OpenAPI. To run another restaurant, deploy a **separate** instance with its own database and environment — this codebase does not host multiple restaurants in one database.
