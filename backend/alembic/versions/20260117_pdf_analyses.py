"""add pdf analyses table

Revision ID: 20260117_pdf_analyses
Revises: 20260117_aia_assumptions
Create Date: 2026-01-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260117_pdf_analyses"
down_revision = "20260117_aia_assumptions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pdf_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("pl_upload_id", sa.Integer(), sa.ForeignKey("uploads.id"), nullable=False),
        sa.Column("bs_upload_id", sa.Integer(), sa.ForeignKey("uploads.id"), nullable=False),
        sa.Column("loans_upload_id", sa.Integer(), sa.ForeignKey("uploads.id"), nullable=True),
        sa.Column("client_view_json", sa.JSON(), nullable=False),
        sa.Column("aia_view_json", sa.JSON(), nullable=False),
        sa.Column("reconciliation_json", sa.JSON(), nullable=False),
        sa.Column("warnings_json", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_pdf_analyses_company_id", "pdf_analyses", ["company_id"])
    op.create_index("ix_pdf_analyses_created_by_user_id", "pdf_analyses", ["created_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_pdf_analyses_created_by_user_id", table_name="pdf_analyses")
    op.drop_index("ix_pdf_analyses_company_id", table_name="pdf_analyses")
    op.drop_table("pdf_analyses")
