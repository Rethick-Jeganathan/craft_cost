from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251014_0002"
down_revision = "20250930_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add row_hash to transactions_raw (idempotent)
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
              SELECT 1 FROM information_schema.columns
              WHERE table_name='transactions_raw' AND column_name='row_hash'
          ) THEN
            ALTER TABLE transactions_raw ADD COLUMN row_hash VARCHAR(64);
          END IF;
        END$$;
        """
    )
    # Index to speed up duplicate checks by (user_id, row_hash)
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'ix_transactions_raw_user_row_hash'
          ) THEN
            CREATE INDEX ix_transactions_raw_user_row_hash ON transactions_raw (user_id, row_hash);
          END IF;
        END$$;
        """
    )

    # Add is_active to transactions (idempotent) and backfill TRUE
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
              SELECT 1 FROM information_schema.columns
              WHERE table_name='transactions' AND column_name='is_active'
          ) THEN
            ALTER TABLE transactions ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
          END IF;
        END$$;
        """
    )
    op.execute("UPDATE transactions SET is_active = TRUE WHERE is_active IS NULL;")


def downgrade() -> None:
    # Drop index and columns (if exist)
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = 'ix_transactions_raw_user_row_hash'
          ) THEN
            DROP INDEX ix_transactions_raw_user_row_hash;
          END IF;
        END$$;
        """
    )
    op.execute("""
        DO $$
        BEGIN
          IF EXISTS (
              SELECT 1 FROM information_schema.columns
              WHERE table_name='transactions_raw' AND column_name='row_hash'
          ) THEN
            ALTER TABLE transactions_raw DROP COLUMN row_hash;
          END IF;
        END$$;
    """)
    op.execute("""
        DO $$
        BEGIN
          IF EXISTS (
              SELECT 1 FROM information_schema.columns
              WHERE table_name='transactions' AND column_name='is_active'
          ) THEN
            ALTER TABLE transactions DROP COLUMN is_active;
          END IF;
        END$$;
    """)
