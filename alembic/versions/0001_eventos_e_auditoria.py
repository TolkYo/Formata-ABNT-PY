"""eventos de uso e auditoria administrativa

Revision ID: 0001
Revises:
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evento_formatacao",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("resultado", sa.String(length=20), nullable=False),
        sa.Column("duracao_ms", sa.Integer(), nullable=True),
        sa.Column("tamanho_bytes", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_evento_data",
        "evento_formatacao",
        ["created_at"],
        postgresql_using="btree",
        postgresql_ops={"created_at": "DESC"},
    )

    op.create_table(
        "admin_auditoria",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("acao", sa.String(length=60), nullable=False),
        sa.Column("alvo_tipo", sa.String(length=40), nullable=True),
        sa.Column("alvo_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("detalhe", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "idx_auditoria_data",
        "admin_auditoria",
        ["created_at"],
        postgresql_using="btree",
        postgresql_ops={"created_at": "DESC"},
    )


def downgrade() -> None:
    op.drop_index("idx_auditoria_data", table_name="admin_auditoria")
    op.drop_table("admin_auditoria")
    op.drop_index("idx_evento_data", table_name="evento_formatacao")
    op.drop_table("evento_formatacao")
