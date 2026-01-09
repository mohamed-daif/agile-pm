"""Initial schema

Revision ID: 001
Create Date: 2026-01-10
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None

def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), default="active"),
        sa.Column("capabilities", sa.JSON, default=[]),
        sa.Column("config", sa.JSON, default={}),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_table(
        "sprints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("goal", sa.Text),
        sa.Column("status", sa.String(20), default="planning"),
        sa.Column("start_date", sa.DateTime),
        sa.Column("end_date", sa.DateTime),
        sa.Column("total_points", sa.Integer, default=0),
        sa.Column("completed_points", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(20), default="not-started"),
        sa.Column("priority", sa.String(5), default="P1"),
        sa.Column("agent_id", sa.String(36), sa.ForeignKey("agents.id")),
        sa.Column("sprint_id", sa.String(36), sa.ForeignKey("sprints.id")),
        sa.Column("story_points", sa.Integer),
        sa.Column("tags", sa.JSON, default=[]),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
    )
    op.create_table(
        "webhooks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("secret", sa.String(64), nullable=False),
        sa.Column("events", sa.JSON, default=[]),
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("description", sa.String(200)),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_table(
        "memory",
        sa.Column("key", sa.String(255), primary_key=True),
        sa.Column("value", sa.JSON),
        sa.Column("ttl", sa.Integer),
        sa.Column("expires_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True),
        sa.Column("hashed_password", sa.String(255)),
        sa.Column("roles", sa.JSON, default=[]),
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime),
        sa.Column("updated_at", sa.DateTime),
    )

def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("memory")
    op.drop_table("webhooks")
    op.drop_table("tasks")
    op.drop_table("sprints")
    op.drop_table("agents")
