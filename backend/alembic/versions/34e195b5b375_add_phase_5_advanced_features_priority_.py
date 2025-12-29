"""Add Phase 5 advanced features: priority, due dates, recurring tasks, tags

Revision ID: 34e195b5b375
Revises: 001
Create Date: 2025-12-30 01:48:23.732945

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '34e195b5b375'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('priority', sa.String(), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('reminder_time', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('tasks', sa.Column('recurrence_type', sa.String(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_interval', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_end_date', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))

    # Add foreign key for parent_task_id
    op.create_foreign_key(
        'fk_tasks_parent_task_id',
        'tasks', 'tasks',
        ['parent_task_id'], ['id']
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])

    # Create task_tags association table
    op.create_table(
        'task_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('ix_task_tags_tag_id', 'task_tags', ['tag_id'])


def downgrade() -> None:
    # Drop task_tags table
    op.drop_index('ix_task_tags_tag_id', table_name='task_tags')
    op.drop_index('ix_task_tags_task_id', table_name='task_tags')
    op.drop_table('task_tags')

    # Drop tags table
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_table('tags')

    # Drop foreign key and columns from tasks table
    op.drop_constraint('fk_tasks_parent_task_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence_interval')
    op.drop_column('tasks', 'recurrence_type')
    op.drop_column('tasks', 'reminder_sent')
    op.drop_column('tasks', 'reminder_time')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority')
