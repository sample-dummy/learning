import sqlmodel

"""Fix spelling mistake

Revision ID: 609147f13ff6
Revises: 181339ccdf5b
Create Date: 2026-10-10 01:23:52.548028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '609147f13ff6'
down_revision: Union[str, Sequence[str], None] = '181339ccdf5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE student AS s
        SET course_id = c.id
        FROM course AS c
        WHERE s.course_id IS NULL
          AND (
              (LOWER(TRIM(s.course)) = 'msc' AND UPPER(c.code) = 'MSC')
              OR
              (LOWER(TRIM(s.course)) = 'entire political science'
               AND UPPER(c.code) = 'EPS')
          )
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE student AS s
        SET course_id = NULL
        FROM course AS c
        WHERE s.course_id = c.id
          AND (
              (LOWER(TRIM(s.course)) = 'msc' AND UPPER(c.code) = 'MSC')
              OR
              (LOWER(TRIM(s.course)) = 'entire political science'
               AND UPPER(c.code) = 'EPS')
          )
    """)
