"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2025-02-28 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Use raw SQL with IF NOT EXISTS so this migration is safe to run
    # even when tables were previously created by SQLAlchemy's create_all().
    op.execute("""
        CREATE TABLE IF NOT EXISTS "user" (
            id UUID NOT NULL,
            email VARCHAR(320) NOT NULL,
            hashed_password VARCHAR(1024) NOT NULL,
            is_active BOOLEAN NOT NULL,
            is_superuser BOOLEAN NOT NULL,
            is_verified BOOLEAN NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email ON "user" (email)
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID NOT NULL,
            user_id UUID NOT NULL,
            role VARCHAR(10) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id UUID NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768),
            PRIMARY KEY (id)
        )
    """)


def downgrade() -> None:
    op.drop_table('knowledge_base')
    op.drop_table('chat_messages')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
