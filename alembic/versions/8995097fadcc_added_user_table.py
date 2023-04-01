"""Added user table

Revision ID: 8995097fadcc
Revises: 
Create Date: 2023-03-27 17:30:28.726113

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '8995097fadcc'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('profile_image', sa.String(length=255), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('location_latitude', sa.Float(), nullable=True),
        sa.Column('location_longitude', sa.Float(), nullable=True),
        sa.Column('date_of_birth', sa.DateTime(), nullable=False),
        sa.Column('gender', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    op.create_table(
        'gallery',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'photo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('caption', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now(), nullable=True),
        sa.Column('gallery_id', sa.Integer(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('like_count', sa.Integer(), default=0),
        sa.Column('dislike_count', sa.Integer(), default=0),
        sa.ForeignKeyConstraint(['gallery_id'], ['gallery.id'], ),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'reaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('photo_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('liked', sa.Boolean(), nullable=False, default=False),
        sa.Column('disliked', sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(['photo_id'], ['photo.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_unique_constraint('uq_reaction_user_photo', 'reaction', ['user_id', 'photo_id'])

    op.create_table(
        'follow',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('followed_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_unique_constraint('uq_follow_follower_followed', 'follow', ['follower_id', 'followed_id'])

    op.create_table(
        'activationtoken',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=36), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    conn = op.get_bind()
    query = """
        INSERT INTO public."user"(
            name,
            email,
            profile_image,
            hashed_password,
            location_latitude,
            location_longitude,
            date_of_birth,
            gender,
            is_active,
            created_at,
            updated_at)
        VALUES(
            'Chris',
            'c@mail.com',
            'profile_pictures/1/2663095343098322638.jpg',
            '$2b$12$G0brEfg3/Z8TlG4.TUIu0O1r22hrCL3JfI7YasB5cg4se3dQyO2rq',
            23.7774522,90.4215606,
            '2022-09-08 00:00:00',
            'male',
            true,
            '2023-04-01 13:13:49.297616',
            '2023-04-01 13:25:22.650657'
        ),
	    (
            'Dean',
            'd@mail.com',
            'profile_pictures/2/adb69e93c5f2WIN.jpg',
            '$2b$12$MB6gxHi4WCADOIlZkUQQt.HgZlKXoJiv7LA6Hu8GkyfTcu4aR6GHa',
            23.7745978,
            90.4219535,
            '2021-12-27 00:00:00',
            'male',
            true,
            '2023-04-01 14:14:05.603054',
            '2023-04-01 16:09:54.343429');
    """
    conn.execute(text(query))

def downgrade():
    op.drop_table('activationtoken')
    op.drop_table('follow')
    op.drop_table('reaction')
    op.drop_table('photo')
    op.drop_table('gallery')
    op.drop_table('user')