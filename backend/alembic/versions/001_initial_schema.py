"""Initial schema: tasks, conversations, messages

Revision ID: 001
Revises:
Create Date: 2025-12-14 00:00:00.000000

Constitution Compliance:
- Principle V: Database as Source of Truth
- Creates tables: tasks, conversations, messages
- Indexes for user_id filtering (security, performance)
- Foreign key constraints for data integrity
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create initial database schema.

    Tables:
    - tasks: User todo items
    - conversations: Chat sessions
    - messages: Individual messages in conversations
    """
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    # Create index on user_id for filtering (Principle IV: Security First)
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])

    # Create composite index for common query pattern (completed tasks per user)
    op.create_index('ix_tasks_user_id_completed', 'tasks', ['user_id', 'completed'])

    # Create trigger to auto-update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_tasks_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER tasks_updated_at_trigger
        BEFORE UPDATE ON tasks
        FOR EACH ROW
        EXECUTE FUNCTION update_tasks_updated_at();
    """)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    # Create index on user_id for filtering
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])

    # Create trigger to auto-update updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_conversations_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER conversations_updated_at_trigger
        BEFORE UPDATE ON conversations
        FOR EACH ROW
        EXECUTE FUNCTION update_conversations_updated_at();
    """)

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for common query patterns
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('ix_messages_user_id', 'messages', ['user_id'])

    # Create composite index for fetching conversation history ordered by time
    op.create_index('ix_messages_conversation_id_created_at', 'messages', ['conversation_id', 'created_at'])


def downgrade() -> None:
    """
    Drop all tables and related objects.

    WARNING: This will delete all data!
    """
    # Drop messages table
    op.drop_index('ix_messages_conversation_id_created_at', table_name='messages')
    op.drop_index('ix_messages_user_id', table_name='messages')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table and trigger
    op.execute('DROP TRIGGER IF EXISTS conversations_updated_at_trigger ON conversations')
    op.execute('DROP FUNCTION IF EXISTS update_conversations_updated_at()')
    op.drop_index('ix_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')

    # Drop tasks table and trigger
    op.execute('DROP TRIGGER IF EXISTS tasks_updated_at_trigger ON tasks')
    op.execute('DROP FUNCTION IF EXISTS update_tasks_updated_at()')
    op.drop_index('ix_tasks_user_id_completed', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
