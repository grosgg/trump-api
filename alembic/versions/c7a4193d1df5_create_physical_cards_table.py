"""Create physical_cards table

Revision ID: c7a4193d1df5
Revises: 0db069533f95
Create Date: 2025-06-28 03:34:19.788248

"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.enums import CardRank, CardSuit


# revision identifiers, used by Alembic.
revision: str = 'c7a4193d1df5'
down_revision: Union[str, Sequence[str], None] = '0db069533f95'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    physical_cards_table = op.create_table(
        "physical_cards",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("suit", sa.Enum(*[suit.name for suit in CardSuit],
                  name='cardsuit'), nullable=False),
        sa.Column("rank", sa.Enum(*[rank.name for rank in CardRank],
                  name='cardrank'), nullable=False),
        sa.Column("deck_number", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("suit", "rank", "deck_number",
                            name="unique_physical_card"),
    )

    for dn in range(1, 3):
        for suit in CardSuit:
            for rank in CardRank:
                op.execute(
                    sa.insert(physical_cards_table).values(
                        id=uuid.uuid4(),
                        suit=suit.name,
                        rank=rank.name,
                        deck_number=dn,
                    )
                )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("physical_cards")
    sa.Enum(*[suit.name for suit in CardSuit],
            name='cardsuit').drop(op.get_bind())
    sa.Enum(*[rank.name for rank in CardRank],
            name='cardrank').drop(op.get_bind())
