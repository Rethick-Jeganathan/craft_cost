from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20250929_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "idempotency",
        sa.Column("key", sa.String(length=255), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=True),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("path", sa.String(length=255), nullable=False),
        sa.Column("body_hash", sa.String(length=64), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("idempotency")
