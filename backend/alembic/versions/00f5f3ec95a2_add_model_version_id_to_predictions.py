"""add model_version_id to predictions

Revision ID: 00f5f3ec95a2
Revises: 16e2b92f6e20
Create Date: 2026-08-03 13:27:43.658769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00f5f3ec95a2'
down_revision: Union[str, None] = '16e2b92f6e20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('predictions', sa.Column('model_version_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_predictions_model_version_id',
        'predictions', 'model_versions',
        ['model_version_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_predictions_model_version_id', 'predictions', type_='foreignkey')
    op.drop_column('predictions', 'model_version_id')