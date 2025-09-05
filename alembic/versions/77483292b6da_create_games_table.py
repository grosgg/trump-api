"""Create games table

Revision ID: 77483292b6da
Revises: aa8736aaafbb
Create Date: 2025-06-26 12:49:05.196179

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.enums import GameVariant, GameStatus


# revision identifiers, used by Alembic.
revision: str = '77483292b6da'
down_revision: Union[str, Sequence[str], None] = 'aa8736aaafbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'games',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('variant', sa.Enum(*[variant.name for variant in GameVariant],
                  name='gamevariant'), nullable=False),
        sa.Column('status', sa.Enum(
            *[status.name for status in GameStatus], name='gamestatus'), nullable=False),
        sa.Column('hands_played', sa.Integer(), nullable=False),
        sa.Column('bank', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('games')
    sa.Enum(*[variant.name for variant in GameVariant],
            name='gamevariant').drop(op.get_bind())
    sa.Enum(*[status.name for status in GameStatus],
            name='gamestatus').drop(op.get_bind())
