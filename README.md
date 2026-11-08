# E-Commerce & Order Management API

A RESTful backend for an online store, built with **Python, FastAPI and PostgreSQL (Neon)**. Customers can browse products, manage a cart, place orders, upload proof of payment and use discount coupons. Administrators manage products, categories, inventory, coupons, orders and payment verification.

This is the capstone project for **GirlsTech Unilorin Bootcamp 1.0** (Backend track).

**Live API:** `https://YOUR-DEPLOYED-URL-HERE`
**Interactive API documentation (Swagger):** `https://YOUR-DEPLOYED-URL-HERE/docs`

---

## Table of contents

1. [Main features](#main-features)
2. [Technologies used](#technologies-used)
3. [Project architecture](#project-architecture)
4. [Database design](#database-design)
5. [Installation and setup](#installation-and-setup)
6. [Environment variables](#environment-variables)
7. [Running the application](#running-the-application)
8. [Running the automated tests](#running-the-automated-tests)
9. [API documentation and Postman collection](#api-documentation-and-postman-collection)
10. [Important business rules and design decisions](#important-business-rules-and-design-decisions)

---

## Main features

**Customers can:**
- Register and log in (JWT authentication)
- View active products and categories
- Search products by name, filter by category and price range, sort by price or date, with pagination
- Manage their own shopping cart
- Place orders from their cart, optionally with a coupon code
- Upload a payment receipt image (JPG, JPEG or PNG) and see the payment status
- Re-upload a receipt after a rejection and see the administrator's reason
- View their order history and track order status
- Cancel eligible orders

**Administrators can:**
- Create, update and deactivate products, and update stock
- Manage categories
- View all orders and update their status
- Review payment receipts: view the image, approve, or reject with a reason
- Create and manage coupons
- View basic system information (counts, orders by status, revenue)

---

## Technologies used

| Purpose | Technology |
|---|---|
| Language | Python 3 |
| Web framework | FastAPI |
| Database | PostgreSQL (hosted on Neon) |
| Database driver | psycopg 3 (parameterised SQL) |
| Migrations | Alembic |
| Authentication | JWT (JSON Web Tokens) |
| Password security | Salted password hashing (plain-text passwords are never stored) |
| Validation | Pydantic |
| API testing | Postman |
| Automated tests | pytest |
| Version control | Git and GitHub |

---

## Project architecture

The project follows **Clean Architecture**. Code is separated into layers, and dependencies only point inward: the domain knows nothing about FastAPI or PostgreSQL.

```
app/
├── domain/                 # Innermost layer: no framework or database imports
│   ├── entities/           # Business objects (User, Product, Order, Coupon...)
│   ├── repositories/       # Repository interfaces (abstract contracts)
│   ├── exceptions.py       # Business errors (no HTTP knowledge)
│   └── storage.py          # Receipt storage interface
├── application/
│   └── use_cases/          # One class per action (RegisterUser, AddToCart, Checkout...)
├── infrastructure/         # Outer layer: the real implementations
│   ├── database/
│   │   ├── connection.py
│   │   └── repositories/   # PostgreSQL repositories (the only place with SQL)
│   └── storage/            # Local receipt image storage
├── api/                    # Presentation layer
│   ├── routes/             # FastAPI routers (thin: validate, call a use case, return)
│   └── dependencies.py     # Wiring: chooses implementations, auth and role guards
├── schemas/                # Pydantic request and response models
├── core/                   # Configuration and security utilities
└── main.py                 # App creation, routers and error handlers
migrations/                 # Alembic migration scripts
scripts/create_admin.py     # Creates an administrator account
tests/                      # Automated tests
docs/erd.png                # Entity Relationship Diagram
```

**How a request flows:** route → use case → repository interface → PostgreSQL repository.
Routes contain no business logic. Use cases depend on repository *interfaces*, so the database could be swapped without changing business rules, and use cases can be tested with fake repositories. `app/api/dependencies.py` is the single place that chooses the PostgreSQL implementation.

**Errors:** the domain raises plain business errors (for example `InsufficientStockError`). `main.py` translates them into HTTP responses (404, 409, 422...). Database errors return a generic message so no SQL or secrets are exposed.

---

## Database design

The full diagram is in [`docs/erd.png`](docs/erd.png).

| Table | Purpose |
|---|---|
| `users` | Accounts, with `role` limited to `customer` or `admin` by a database check |
| `categories` | Product categories (unique name) |
| `products` | Price, stock, unique SKU, `is_active` flag, creation date |
| `carts` | One cart per customer (`user_id` is unique) |
| `cart_items` | Items in a cart (one row per product per cart) |
| `orders` | Status, subtotal, discount, total, coupon, idempotency key |
| `order_items` | Product name and unit price copied at purchase time |
| `payments` | One row per receipt submission, with status and rejection reason |
| `coupons` | Code, type, value, expiry, usage limit, minimum order, active flag |
| `coupon_usage` | One row per order that used a coupon |

**Integrity is enforced in the database as well as in code:**
- Unique email, product SKU, category name and coupon code
- `CHECK (stock >= 0)`, `CHECK (price >= 0)`, `CHECK (quantity > 0)`
- `CHECK` on order and payment status values and on percentage coupons (at most 100)
- `UNIQUE (cart_id, product_id)` so the same product cannot appear twice in a cart
- `UNIQUE (user_id, idempotency_key)` on orders to prevent duplicate checkouts
- Foreign keys between all related tables

All schema changes are managed with Alembic migrations in `migrations/versions/`.

---

## Installation and setup

**Prerequisites:** Python 3.11 or newer, Git, and a PostgreSQL database (this project uses a free [Neon](https://neon.tech) database).

```bash
# 1. Clone the repository
git clone https://github.com/Temitope-213/ecommerce-order-management-api.git
cd ecommerce-order-management-api

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your environment file
#    Copy .env.example to .env and fill in your own values (see next section)

# 5. Create the database tables
alembic upgrade head

# 6. Create an administrator account (interactive prompt)
python -m scripts.create_admin
```

Customers register through the API. An administrator can **only** be created with the script in step 6, never through public registration.

---

## Environment variables

Copy `.env.example` to `.env` and set:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string (from your Neon dashboard) |
| `JWT_SECRET_KEY` | A long random secret used to sign tokens. Keep it private. |
| `RECEIPTS_DIR` | Folder where uploaded receipt images are stored (default `uploads/receipts`) |

Real secrets are never committed: `.env` and `uploads/` are listed in `.gitignore`.

---

## Running the application

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger documentation: http://127.0.0.1:8000/docs

---

## Running the automated tests

```bash
pytest
```

The tests cover authentication and authorization, products, cart, order creation, stock validation, coupon calculations, payment processing and important business rules, including failure cases.

---

## API documentation and Postman collection

- **Swagger / OpenAPI:** available at `/docs` on any running instance.
- **Postman collection:** [`postman/ecommerce-api.postman_collection.json`](postman/ecommerce-api.postman_collection.json), organised into the folders Authentication, Products, Categories, Shopping Cart, Orders, Payments, Coupons and Admin Operations. It includes both successful and failing scenarios (duplicate email, wrong password, missing token, customer calling an admin endpoint, over-stock cart, empty-cart checkout, expired coupon, cancelling a delivered order, accessing another customer's order, and concurrent purchase of the last item).

**Endpoint overview** (see `/docs` for exact request and response formats):

| Area | Endpoints |
|---|---|
| Authentication | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Categories | `GET /categories`, `POST /categories`, `PUT /categories/{id}`, `DELETE /categories/{id}` |
| Products | `GET /products` (search, filter, sort, pagination), `GET /products/{id}`, `POST /products`, `PUT /products/{id}`, `PATCH /products/{id}/stock`, `DELETE /products/{id}` (deactivates) |
| Cart | `GET /cart`, `POST /cart/items`, `PUT /cart/items/{product_id}`, `DELETE /cart/items/{product_id}`, `DELETE /cart` |
| Orders | `POST /orders/checkout`, `GET /orders`, `GET /orders/{id}`, `POST /orders/{id}/cancel` |
| Payments (customer) | `POST /orders/{id}/payment` (upload receipt), `GET /orders/{id}/payment` |
| Admin orders | `GET /admin/orders`, `GET /admin/orders/{id}`, `PATCH /admin/orders/{id}/status` |
| Admin payments | `GET /admin/payments`, `GET /admin/payments/{id}`, `GET /admin/payments/{id}/receipt`, `POST /admin/payments/{id}/approve`, `POST /admin/payments/{id}/reject` |
| Admin coupons | `POST/GET /admin/coupons`, `GET/PUT/DELETE /admin/coupons/{id}` |
| Admin info | `GET /admin/system-info` |

---

## Important business rules and design decisions

**Security**
- Passwords are hashed before storage and never returned in any response.
- Public registration always creates a `customer`. The role is never taken from the request.
- Role checks happen on the backend. Every admin route depends on `require_admin`, which reads the role from the database, not from the client.
- Authentication failures return one generic message (401), so attackers cannot tell whether a token was missing, invalid or expired. A customer calling an admin route gets 403.
- Cart and order routes never accept a user id. The owner always comes from the JWT, so a customer cannot reach another customer's data. Someone else's order returns 404, the same as a missing order.
- Uploaded receipts are checked by their real file signature (not the file name), limited to 5 MB, stored under random names, and only administrators can fetch them.

**Products and cart**
- Customers can only see and buy active products. "Deleting" a product deactivates it so that past orders keep working.
- Adding the same product again increases the quantity of the existing cart line. The total quantity can never exceed available stock.

**Checkout (the core of the system)**
- **Transactions:** order creation, order items, stock deduction, coupon use and cart clearing all happen in one database transaction. If any step fails, everything rolls back.
- **Overselling prevention:** stock is deducted with one atomic statement, `UPDATE products SET stock = stock - qty WHERE id = ... AND stock >= qty`. When two customers buy the last item at the same moment, PostgreSQL serialises the updates and only one succeeds. The other receives 409 Conflict. A `CHECK (stock >= 0)` constraint is a second safety net.
- **Idempotency:** checkout requires an `Idempotency-Key` header. Sending the same key again (double click, network retry) returns the original order instead of creating a second one. The customer's cart row is locked during checkout so two simultaneous retries cannot both pass, and a unique constraint on `(user_id, idempotency_key)` guarantees it at the database level.
- **Backend pricing:** the client never sends prices. Prices and names are read from the database inside the transaction and copied into `order_items`, so later changes to a product never alter past orders.
- **Empty carts** cannot be checked out.

**Order statuses:** `PENDING`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`. Allowed transitions:

```
PENDING -> CONFIRMED | CANCELLED
CONFIRMED -> PROCESSING | CANCELLED
PROCESSING -> SHIPPED
SHIPPED -> DELIVERED
DELIVERED, CANCELLED -> (final)
```

A delivered order cannot be cancelled. Cancelling returns the stock and releases any coupon use, in one transaction. An order cannot become `CONFIRMED` or `PROCESSING` without an approved payment.

**Payments (receipt upload)**
1. The customer places an order and sees the total to pay.
2. The customer pays externally, then uploads a receipt image. The payment becomes `UNDER_REVIEW`. The amount is taken from the order, never from the client.
3. An administrator views the image and approves or rejects it. A rejection requires a reason.
4. Approval sets the payment to `APPROVED` and the order to `CONFIRMED`. Rejection sets `REJECTED`, the customer sees the reason and can upload a new receipt.
- Statuses: `NOT_SUBMITTED` (no receipt yet), `UNDER_REVIEW`, `APPROVED`, `REJECTED`.
- Every submission is a new row, which gives a full verification history. Reviews lock the order and payment rows so two admins cannot approve the same payment twice.

**Coupons**
- Types: percentage (1 to 100) or fixed amount. Codes are stored in uppercase.
- A coupon is rejected if it is inactive, expired, below the minimum order amount, over its usage limit, or already used by that customer.
- Validation and usage recording happen inside the checkout transaction, and the coupon row is locked so the last remaining use cannot be taken twice.
- The discount can never exceed the subtotal, so the final total is never negative.

**Design decisions and known limitations**
- Receipt images are stored on the server's local disk through a `ReceiptStorage` interface. On hosting platforms with temporary disks, files may be lost when the service restarts. Moving to cloud storage only requires a new implementation of that interface and one changed line in `dependencies.py`.
- Raw parameterised SQL (psycopg) is used instead of an ORM so transactions and row locking are explicit and visible.
