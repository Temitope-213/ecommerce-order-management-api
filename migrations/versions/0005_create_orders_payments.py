"""create orders, order items, payments and coupon usage

Revision ID: 0005
Revises: 0004
"""
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE orders (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                CHECK (status IN ('PENDING', 'CONFIRMED', 'PROCESSING',
                                  'SHIPPED', 'DELIVERED', 'CANCELLED')),
            subtotal NUMERIC(10, 2) NOT NULL CHECK (subtotal >= 0),
            discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0
                CHECK (discount_amount >= 0),
            total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
            coupon_id INTEGER REFERENCES coupons(id),
            idempotency_key VARCHAR(100),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (user_id, idempotency_key)
        )
    """)
    op.execute("CREATE INDEX idx_orders_user ON orders (user_id)")
    op.execute("""
        CREATE TABLE order_items (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
            product_name VARCHAR(200) NOT NULL,
            unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
            quantity INTEGER NOT NULL CHECK (quantity > 0)
        )
    """)
    op.execute("""
        CREATE TABLE payments (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
            status VARCHAR(20) NOT NULL DEFAULT 'UNDER_REVIEW'
                CHECK (status IN ('NOT_SUBMITTED', 'UNDER_REVIEW',
                                  'APPROVED', 'REJECTED')),
            receipt_path VARCHAR(255) NOT NULL,
            rejection_reason TEXT,
            reviewed_by INTEGER REFERENCES users(id),
            reviewed_at TIMESTAMPTZ,
            submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_payments_order ON payments (order_id)")
    op.execute("""
        CREATE TABLE coupon_usage (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            coupon_id INTEGER NOT NULL REFERENCES coupons(id),
            user_id INTEGER NOT NULL REFERENCES users(id),
            order_id INTEGER NOT NULL UNIQUE REFERENCES orders(id) ON DELETE CASCADE,
            used_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_coupon_usage_coupon ON coupon_usage (coupon_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS coupon_usage")
    op.execute("DROP TABLE IF EXISTS payments")
    op.execute("DROP TABLE IF EXISTS order_items")
    op.execute("DROP TABLE IF EXISTS orders")