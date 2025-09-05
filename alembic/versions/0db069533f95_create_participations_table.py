"""Create participations table

Revision ID: 0db069533f95
Revises: 77483292b6da
Create Date: 2025-06-27 00:21:13.740299

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.enums import ParticipationStatus

# revision identifiers, used by Alembic.
revision: str = '0db069533f95'
down_revision: Union[str, Sequence[str], None] = '77483292b6da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'participations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum(
            *[status.name for status in ParticipationStatus], name='participationstatus'), nullable=False),
        sa.Column('bet', sa.Integer(), nullable=False),
        sa.Column('cash', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('game_id', sa.Uuid()),
        sa.Column('user_id', sa.Uuid()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['game_id'], ['games.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('participations')
    sa.Enum(*[status.name for status in ParticipationStatus],
            name='participationstatus').drop(op.get_bind())
