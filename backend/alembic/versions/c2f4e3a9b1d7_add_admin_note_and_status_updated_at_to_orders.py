"""Add admin order fields and enum values

Revision ID: c2f4e3a9b1d7
Revises: 98975f86325b
Create Date: 2026-03-18 08:30:00.000000
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c2f4e3a9b1d7"
down_revision: Union[str, Sequence[str], None] = "98975f86325b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Keep migration idempotent for environments where schema may drift from Alembic history.
    op.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS admin_note VARCHAR(1000)
        """)
    op.execute("""
        ALTER TABLE orders
        ADD COLUMN IF NOT EXISTS status_updated_at TIMESTAMPTZ
        """)

    # Ensure enum values exist for current domain model.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'orderstatus') THEN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_enum
                    WHERE enumlabel = 'DELIVERED'
                      AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'orderstatus')
                ) THEN
                    ALTER TYPE orderstatus ADD VALUE 'DELIVERED';
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_enum
                    WHERE enumlabel = 'REFUNDING'
                      AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'orderstatus')
                ) THEN
                    ALTER TYPE orderstatus ADD VALUE 'REFUNDING';
                END IF;
            END IF;
        END
        $$;
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE orders
        DROP COLUMN IF EXISTS status_updated_at
        """)
    op.execute("""
        ALTER TABLE orders
        DROP COLUMN IF EXISTS admin_note
        """)

    # Enum value removal is intentionally not attempted for PostgreSQL compatibility.
