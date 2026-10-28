import sqlmodel

"""Backfill students table

Revision ID: 181339ccdf5b
Revises: 78738f73dd72
Create Date: 2026-10-10 01:13:24.946986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '181339ccdf5b'
down_revision: Union[str, Sequence[str], None] = '78738f73dd72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    UPDATE student
    SET course_id = course.id
    FROM course
    WHERE student.course = course.code
""")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        UPDATE student
        SET course_id = NULL
        FROM course
        WHERE student.course = course.code
          AND student.course_id = course.id
    """)
