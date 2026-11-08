"""create coupons

Revision ID: 0003
Revises: 0002
"""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE coupons (
            id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            code VARCHAR(50) NOT NULL UNIQUE,
            discount_type VARCHAR(20) NOT NULL
                CHECK (discount_type IN ('percentage', 'fixed')),
            discount_value NUMERIC(10, 2) NOT NULL CHECK (discount_value > 0),
            expires_at TIMESTAMPTZ NOT NULL,
            max_uses INTEGER NOT NULL CHECK (max_uses > 0),
            min_order_amount NUMERIC(10, 2) NOT NULL DEFAULT 0
                CHECK (min_order_amount >= 0),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT percentage_in_range
                CHECK (discount_type <> 'percentage' OR discount_value <= 100)
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS coupons")