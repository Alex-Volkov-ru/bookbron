"""Initial migration

Revision ID: 3452e17456ab
Revises: 
Create Date: 2026-01-15 12:29:43.314721

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3452e17456ab'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types (if not exists)
    op.execute("DO $$ BEGIN CREATE TYPE userrole AS ENUM ('admin', 'manager', 'user'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE bookingstatus AS ENUM ('pending', 'confirmed', 'cancelled', 'completed'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('tg_id', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_phone'), 'users', ['phone'], unique=True)
    op.create_index(op.f('ix_users_tg_id'), 'users', ['tg_id'], unique=True)
    
    # Create cafes table
    op.create_table(
        'cafes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photo', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cafes_id'), 'cafes', ['id'], unique=False)
    op.create_index(op.f('ix_cafes_name'), 'cafes', ['name'], unique=False)
    
    # Create cafe_managers association table
    op.create_table(
        'cafe_managers',
        sa.Column('cafe_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cafe_id'], ['cafes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('cafe_id', 'user_id')
    )
    
    # Create tables table
    op.create_table(
        'tables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cafe_id', sa.Integer(), nullable=False),
        sa.Column('seats_count', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cafe_id'], ['cafes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tables_id'), 'tables', ['id'], unique=False)
    op.create_index(op.f('ix_tables_cafe_id'), 'tables', ['cafe_id'], unique=False)
    
    # Create slots table
    op.create_table(
        'slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cafe_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cafe_id'], ['cafes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_slots_id'), 'slots', ['id'], unique=False)
    op.create_index(op.f('ix_slots_cafe_id'), 'slots', ['cafe_id'], unique=False)
    
    # Create dishes table
    op.create_table(
        'dishes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photo', sa.String(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dishes_id'), 'dishes', ['id'], unique=False)
    op.create_index(op.f('ix_dishes_name'), 'dishes', ['name'], unique=False)
    
    # Create cafe_dishes association table
    op.create_table(
        'cafe_dishes',
        sa.Column('dish_id', sa.Integer(), nullable=False),
        sa.Column('cafe_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['cafe_id'], ['cafes.id'], ),
        sa.ForeignKeyConstraint(['dish_id'], ['dishes.id'], ),
        sa.PrimaryKeyConstraint('dish_id', 'cafe_id')
    )
    
    # Create actions table
    op.create_table(
        'actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('photo', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_actions_id'), 'actions', ['id'], unique=False)
    
    # Create cafe_actions association table
    op.create_table(
        'cafe_actions',
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('cafe_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['action_id'], ['actions.id'], ),
        sa.ForeignKeyConstraint(['cafe_id'], ['cafes.id'], ),
        sa.PrimaryKeyConstraint('action_id', 'cafe_id')
    )
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('cafe_id', sa.Integer(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.Column('slot_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('reminder_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['cafe_id'], ['cafes.id'], ),
        sa.ForeignKeyConstraint(['slot_id'], ['slots.id'], ),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    op.create_index(op.f('ix_bookings_user_id'), 'bookings', ['user_id'], unique=False)
    op.create_index(op.f('ix_bookings_cafe_id'), 'bookings', ['cafe_id'], unique=False)
    op.create_index(op.f('ix_bookings_table_id'), 'bookings', ['table_id'], unique=False)
    op.create_index(op.f('ix_bookings_slot_id'), 'bookings', ['slot_id'], unique=False)
    op.create_index(op.f('ix_bookings_date'), 'bookings', ['date'], unique=False)
    
    # Create booking_dishes table
    op.create_table(
        'booking_dishes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('dish_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.ForeignKeyConstraint(['dish_id'], ['dishes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_booking_dishes_id'), 'booking_dishes', ['id'], unique=False)
    op.create_index(op.f('ix_booking_dishes_booking_id'), 'booking_dishes', ['booking_id'], unique=False)
    op.create_index(op.f('ix_booking_dishes_dish_id'), 'booking_dishes', ['dish_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_booking_dishes_dish_id'), table_name='booking_dishes')
    op.drop_index(op.f('ix_booking_dishes_booking_id'), table_name='booking_dishes')
    op.drop_index(op.f('ix_booking_dishes_id'), table_name='booking_dishes')
    op.drop_table('booking_dishes')
    
    op.drop_index(op.f('ix_bookings_date'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_slot_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_table_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_cafe_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_user_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')
    
    op.drop_table('cafe_actions')
    op.drop_index(op.f('ix_actions_id'), table_name='actions')
    op.drop_table('actions')
    
    op.drop_table('cafe_dishes')
    op.drop_index(op.f('ix_dishes_name'), table_name='dishes')
    op.drop_index(op.f('ix_dishes_id'), table_name='dishes')
    op.drop_table('dishes')
    
    op.drop_index(op.f('ix_slots_cafe_id'), table_name='slots')
    op.drop_index(op.f('ix_slots_id'), table_name='slots')
    op.drop_table('slots')
    
    op.drop_index(op.f('ix_tables_cafe_id'), table_name='tables')
    op.drop_index(op.f('ix_tables_id'), table_name='tables')
    op.drop_table('tables')
    
    op.drop_table('cafe_managers')
    op.drop_index(op.f('ix_cafes_name'), table_name='cafes')
    op.drop_index(op.f('ix_cafes_id'), table_name='cafes')
    op.drop_table('cafes')
    
    op.drop_index(op.f('ix_users_tg_id'), table_name='users')
    op.drop_index(op.f('ix_users_phone'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS bookingstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
