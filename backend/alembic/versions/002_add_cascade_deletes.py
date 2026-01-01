"""Add CASCADE to foreign keys for automatic cleanup

Revision ID: 002
Revises: 34e195b5b375
Create Date: 2025-12-30 02:45:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '34e195b5b375'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing foreign keys
    op.drop_constraint('task_tags_task_id_fkey', 'task_tags', type_='foreignkey')
    op.drop_constraint('task_tags_tag_id_fkey', 'task_tags', type_='foreignkey')

    # Recreate with CASCADE
    op.create_foreign_key(
        'task_tags_task_id_fkey',
        'task_tags', 'tasks',
        ['task_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'task_tags_tag_id_fkey',
        'task_tags', 'tags',
        ['tag_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop CASCADE foreign keys
    op.drop_constraint('task_tags_task_id_fkey', 'task_tags', type_='foreignkey')
    op.drop_constraint('task_tags_tag_id_fkey', 'task_tags', type_='foreignkey')

    # Recreate without CASCADE
    op.create_foreign_key(
        'task_tags_task_id_fkey',
        'task_tags', 'tasks',
        ['task_id'], ['id']
    )
    op.create_foreign_key(
        'task_tags_tag_id_fkey',
        'task_tags', 'tags',
        ['tag_id'], ['id']
    )
