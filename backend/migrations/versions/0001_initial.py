"""Esquema inicial de QuickShop."""
from alembic import op
import sqlalchemy as sa
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def timestamps():
    return [sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())]

def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(254), nullable=False, unique=True), sa.Column("name", sa.String(100), nullable=False), sa.Column("password_hash", sa.String(128), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("token_version", sa.Integer(), nullable=False), *timestamps(), sa.CheckConstraint("role IN ('cliente','administrador')"))
    op.create_table("password_resets", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), unique=True, nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("used_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])
    op.create_table("products", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False), sa.Column("description", sa.String(2000), nullable=False), sa.Column("price", sa.Numeric(10,2), nullable=False), sa.Column("stock", sa.Integer(), nullable=False), sa.Column("image_url", sa.String(2000), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False), *timestamps(), sa.CheckConstraint("price > 0"), sa.CheckConstraint("stock >= 0"))
    op.create_table("carts", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True))
    op.create_table("cart_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.UniqueConstraint("cart_id","product_id"), sa.CheckConstraint("quantity > 0"))
    op.create_table("orders", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("total", sa.Numeric(20,2), nullable=False), *timestamps(), sa.CheckConstraint("status IN ('pendiente','confirmado','enviado','entregado','cancelado')"), sa.CheckConstraint("total >= 0"))
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_table("order_items", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False), sa.Column("product_name", sa.String(150), nullable=False), sa.Column("unit_price", sa.Numeric(10,2), nullable=False), sa.Column("quantity", sa.Integer(), nullable=False), sa.CheckConstraint("quantity > 0"), sa.CheckConstraint("unit_price > 0"))

def downgrade():
    for table in ("order_items", "orders", "cart_items", "carts", "products", "password_resets", "users"):
        op.drop_table(table)
