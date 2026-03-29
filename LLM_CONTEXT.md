# Restro backend — full context for LLMs / handoff

Copy this file (or the whole `restro_backend/` tree excluding `.venv`) when onboarding another assistant. **Last updated after model/admin/Celery/ASGI changes (see migrations `0003_*` where applicable).**

---

## 1. What this project is

- **Django + Django REST Framework** API for **one restaurant per database** (not multi-tenant SaaS).
- **Schema, admin, and serializer stubs exist**; **almost no business logic or HTTP endpoints** are implemented yet (`views.py` / `urls.py` are mostly empty).
- **Custom user model:** `accounts.User` (email login, roles: manager / captain / kitchen).
- **Branding (logos, themes)** is intended to live in the **frontend**. `RestaurantConfig` holds **operational** venue data only (name, contact, address, tax, currency, timezone).
- **Secrets** (Razorpay, Swiggy, Zomato keys, commissions) are read from **environment variables** via `config/settings/base.py` — **not** stored on `RestaurantConfig`. Payment rows **snapshot** commission at transaction time (see `Payment`).
- **No `audit` app (MVP):** structured audit logging was removed to reduce scope. Add a dedicated app later or rely on server / reverse-proxy logs for accountability if needed.

---

## 2. Tech stack (`requirements.txt`)

- Django 4.2–5.x, djangorestframework, djangorestframework-simplejwt, django-cors-headers, python-dotenv
- channels, channels-redis (WebSockets — **Redis expected**)
- celery[redis], redis — **`config/celery.py`** defines the Celery app; `config/__init__.py` exposes `celery_app` for autodiscovery
- psycopg2-binary (for **future** PostgreSQL; DB is SQLite today)

---

## 3. Directory layout (ignore `.venv/`)

```
restro_backend/
├── manage.py
├── requirements.txt
├── README.md
├── LLM_CONTEXT.md          ← this file
├── .gitignore
├── .env                    ← gitignored; see README / section 9
├── config/
│   ├── __init__.py         ← imports celery_app from .celery
│   ├── celery.py           ← Celery app: namespace CELERY, autodiscover_tasks
│   ├── settings/
│   │   ├── base.py         ← main settings + env-backed secrets + SQLite
│   │   ├── development.py  ← DEBUG=True, imports base
│   │   └── production.py   ← DEBUG from env, SECURE_SSL_REDIRECT
│   ├── urls.py             ← admin + api/v1/* includes (stubs)
│   ├── wsgi.py             ← defaults to production settings
│   └── asgi.py             ← defaults to production settings (Channels / live deploy)
└── apps/
    ├── accounts/           # User model, managers
    ├── venue/              # RestaurantConfig (singleton), Table, selectors
    ├── menu/               # Category, MenuItem
    ├── sessions/           # app label: table_sessions — TableSession
    ├── orders/             # Order, OrderItem
    ├── billing/            # Bill, Payment
    └── analytics/          # DailyAnalytics, ItemAnalytics
```

**Removed earlier:** `apps/integrations`. **No** `apps/venue/env.py` — use `django.conf.settings` for keys.

---

## 4. Django settings highlights (`config/settings/base.py`)

| Area | Detail |
|------|--------|
| `AUTH_USER_MODEL` | `accounts.User` |
| `DATABASES` | **SQLite** `BASE_DIR / "db.sqlite3"` (PostgreSQL planned later) |
| `REST_FRAMEWORK` | JWT auth default; `IsAuthenticated` default permission |
| `CHANNEL_LAYERS` | `channels_redis` → `REDIS_URL` |
| `CELERY_*` | `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` → `REDIS_URL` |
| `CORS_ALLOWED_ORIGINS` | From env, comma-separated |
| Env-backed | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `SWIGGY_*`, `ZOMATO_*`, `RAZORPAY_*`, commission %, `REDIS_URL`, `CORS_ALLOWED_ORIGINS` |

`manage.py` sets `DJANGO_SETTINGS_MODULE=config.settings.development`.

**ASGI default:** `config/asgi.py` sets **`config.settings.production`** so WebSocket servers are not pinned to development settings.

**Celery:** `config/celery.py` defaults `DJANGO_SETTINGS_MODULE` to **development** for local workers (matches common dev workflow).

---

## 5. URL routing (`config/urls.py`)

- `/admin/`
- `/api/v1/<app>/` → each app’s `urls.py` (currently **`urlpatterns = []`** or commented placeholders)

**Not wired:** SimpleJWT token obtain/refresh URLs (package installed, routes not added).

---

## 6. Models and relationships

**Convention:** UUID primary keys on domain models unless noted.

### `venue` (label `venue`)

- **`RestaurantConfig`** — **exactly one row** per DB (enforced: admin cannot add second row; use `venue.selectors.get_restaurant_config()` which raises if 0 or >1 rows).  
  **Fields:** `name`, `legal_name`, `phone`, `email`, `address`, `timezone`, `tax_rate`, `currency`, `updated_at`.  
  **No FK** to other models (single-venue-per-DB).

- **`Table`** — `table_number`, `seating_capacity`, **`section`** (`indoor` | `outdoor` | `vip` | `bar`, default `indoor`), **`status`** (`empty` | `occupied` | **`bill_requested`** | `cleaning` | **`reserved`**), `qr_token`, `qr_token_expires_at`, timestamps.  
  - **`bill_requested`:** distinct from `occupied` so QR flow can show “bill in progress” and block new orders.  
  - **`reserved`:** holds table before guests are seated.

### `accounts` (label `accounts`)

- **`User`** — `email` (USERNAME_FIELD), `phone`, `name`, `role`, `is_active`, `is_staff`, `created_at`, password from `AbstractBaseUser`.

### `menu` (label `menu`)

- **`Category`** — `name`, `sort_order`, `is_active`
- **`MenuItem`** — FK **`Category`**, `name`, **`description`** (nullable), `price`, **`cost_price`** (nullable, for margin analytics), **`image_url`** (nullable), **`prep_time_mins`** (default 15, for KDS urgency), `is_vegetarian`, `is_vegan`, `availability`, `is_active`, timestamps

### `sessions` (label **`table_sessions`** — important for string refs)

- **`TableSession`** — FK **`venue.Table`**, `qr_token_used`, `status`, `opened_at`, `bill_requested_at`, `paid_at`, `closed_at`, FK **`User`** `captain` (nullable), **`notes`** (nullable; captain context, e.g. birthday / VIP)

### `orders` (label `orders`)

- **`Order`** — FK **`table_sessions.TableSession`** `session` (nullable for non–dine-in), **`external_order_id`** (nullable, **unique** — Swiggy/Zomato dedup key for idempotent webhooks), `order_number`, `channel`, `status`, `subtotal`, `tax_amount`, `discount_amount`, `total_amount`, **`special_request`** (nullable — QR / customer notes for KDS), FK **`User`** `confirmed_by`, `created_at`, `confirmed_at`, `ready_at`, `served_at`
- **`OrderItem`** — FK **`Order`** (CASCADE), FK **`menu.MenuItem`** (PROTECT), snapshot `name`, `unit_price`, `quantity`, `subtotal`

### `billing` (label `billing`)

- **`Bill`** — **OneToOne** **`table_sessions.TableSession`**, totals, `tip_amount`, `amount_paid`, `status`, FK **`User`** `locked_by`, `locked_at`, timestamps
- **`Payment`** — FK **`Bill`**, `amount`, `method`, `gateway`, **`commission_pct`**, **`commission_amount`**, **`net_settlement`** (snapshot at payment time; dine-in typically 0 / amount), **`razorpay_order_id`**, **`razorpay_payment_id`**, **`razorpay_signature`** (nullable — HMAC verification), `status`, FK **`User`** `collected_by`, timestamps

### `analytics` (label `analytics`)

- **`DailyAnalytics`** — one row per `date`; revenue splits, counts, `payment_method_breakdown` JSON
- **`ItemAnalytics`** — FK **`menu.MenuItem`**, `date`, `quantity_sold`, `revenue`; unique `(menu_item, date)`  
  *(Margin reporting can use `MenuItem.cost_price` vs revenue; no `margin_amount` column on this model currently.)*

### Relationship summary

```
RestaurantConfig (standalone singleton)
Table ← TableSession → Order (optional session) → OrderItem → MenuItem → Category
TableSession 1:1 Bill → Payment
User ← captain, confirmed_by, locked_by, collected_by
```

---

## 7. Migrations

Apps progressed through initial migrations, trims, and feature migrations (menu, orders, billing, venue, sessions, etc.). The **`audit` app was removed** for MVP (run `python manage.py migrate audit zero` on older databases before deleting the app code, then remove `apps.audit` from `INSTALLED_APPS`).  
Run: `python manage.py migrate`

---

## 8. Per-app files (typical pattern)

| File | Role |
|------|------|
| `models.py` | Domain models |
| `admin.py` | Django admin (registered) |
| `serializers.py` | DRF `ModelSerializer` stubs (`__all__` or explicit fields) — **may lag new fields until updated** |
| `views.py` | Stub / docstring only |
| `urls.py` | Empty `urlpatterns` |
| `apps.py` | AppConfig; **`sessions`** uses label `table_sessions` |

**Venue extras:** `selectors.py` → `get_restaurant_config()`.

---

## 9. Environment (`.env` — not in git)

Typical keys: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `REDIS_URL`, `CORS_ALLOWED_ORIGINS`, `SWIGGY_API_KEY`, `ZOMATO_API_KEY`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `SWIGGY_COMMISSION_PCT`, `ZOMATO_COMMISSION_PCT`. PostgreSQL vars commented for later.

---

## 10. What is intentionally NOT done yet

- No real **API views** or **routing** for business flows
- No **JWT URL** endpoints
- **Celery worker process** not configured in deploy docs (app module **exists**; run e.g. `celery -A config worker`)
- No **Channels** consumers / routing (Redis still configured)
- **Production** settings minimal (SSL redirect only); no `STATIC_ROOT`, full security bundle, etc.
- SQLite **not** ideal for heavy concurrent production (planned move to PostgreSQL)

---

## 11. Commands

```bash
cd restro_backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
set DJANGO_SETTINGS_MODULE=config.settings.development   # Windows
python manage.py migrate
python manage.py createsuperuser   # requires email, phone, name
python manage.py runserver
```

**Celery (example):** `celery -A config worker -l info` (with Redis and `DJANGO_SETTINGS_MODULE` set as needed).

---

## 12. Design decisions (for continuity)

- **Domain apps**, not role-based apps.
- **Single `RestaurantConfig`** row; no `Table → RestaurantConfig` FK (whole DB = one venue).
- **Order** may have `session=NULL` for delivery/web-style orders; **`external_order_id`** unique prevents duplicate aggregator orders on replayed webhooks.
- **`special_request`** on **Order** for customer/KDS notes; **`TableSession.notes`** for captain/internal context.
- **Bill** is 1:1 with **TableSession**; multiple **Orders** per session need clear **business rules** when aggregating into one bill.
- **Table.status `bill_requested`** vs **`occupied`** drives QR “menu blocked” vs still ordering; **`reserved`** for pre-arrival holds.
- **Table.section** is a fixed enum (`indoor` / `outdoor` / `vip` / `bar`).
- **Payment** stores **commission + Razorpay ids** as snapshots for history and verification.
- **Table** public serializers omit `qr_token` (see `venue/serializers.py`); staff serializer includes full row.
- **`MenuItem.prep_time_mins`** supports KDS timing (blue / orange / red) in the app layer.

---

*End of handoff document.*
