"""add aia assumptions and runs

Revision ID: 20260117_aia_assumptions
Revises: 20260115_add_auth_tables
Create Date: 2026-01-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260117_aia_assumptions"
down_revision = "20260115_add_auth_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assumption_sets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("scenario_key", sa.String(length=100), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_assumption_sets_company_id", "assumption_sets", ["company_id"])
    op.create_index("ix_assumption_sets_created_by_user_id", "assumption_sets", ["created_by_user_id"])
    op.create_index("ix_assumption_sets_status", "assumption_sets", ["status"])

    op.create_table(
        "simulation_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("assumption_set_id", sa.Integer(), sa.ForeignKey("assumption_sets.id"), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("horizon_months", sa.Integer(), nullable=False, server_default="12"),
        sa.Column("horizon_years", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_simulation_runs_company_id", "simulation_runs", ["company_id"])
    op.create_index("ix_simulation_runs_assumption_set_id", "simulation_runs", ["assumption_set_id"])
    op.create_index("ix_simulation_runs_created_by_user_id", "simulation_runs", ["created_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_simulation_runs_created_by_user_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_assumption_set_id", table_name="simulation_runs")
    op.drop_index("ix_simulation_runs_company_id", table_name="simulation_runs")
    op.drop_table("simulation_runs")

    op.drop_index("ix_assumption_sets_status", table_name="assumption_sets")
    op.drop_index("ix_assumption_sets_created_by_user_id", table_name="assumption_sets")
    op.drop_index("ix_assumption_sets_company_id", table_name="assumption_sets")
    op.drop_table("assumption_sets")
