"""Create game_cards table

Revision ID: b6fefa705edf
Revises: c7a4193d1df5
Create Date: 2025-06-28 05:46:12.045980

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from alembic import op

from app.enums import CardLocation, CardRank, CardSuit

# revision identifiers, used by Alembic.
revision: str = 'b6fefa705edf'
down_revision: Union[str, Sequence[str], None] = 'c7a4193d1df5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'game_cards',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('game_id', sa.Uuid(), nullable=False),
        sa.Column("suit", pgEnum(*[suit.name for suit in CardSuit],
                                 name='cardsuit', create_type=False), nullable=False),
        sa.Column("rank", pgEnum(*[rank.name for rank in CardRank],
                                 name='cardrank', create_type=False), nullable=False),
        sa.Column('physical_card_id', sa.Uuid(), nullable=False),
        sa.Column('location_type', sa.Enum(
            *[location.name for location in CardLocation],
            name='cardlocation'), nullable=False),
        sa.Column('holder_id', sa.Uuid(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['physical_card_id'], [
                                'physical_cards.id'], ondelete='CASCADE')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('game_cards')
    sa.Enum(*[location.name for location in CardLocation],
            name='cardlocation').drop(op.get_bind())
