from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from .database import get_db
from .models import Product, Cart, CartItem, Order, OrderItem, User
from .schemas import ProductInput, ProductOut, CartAddInput, QuantityInput, CartOut, OrderOut, OrderStatusInput
from .security import current_user, admin_user, client_user

router = APIRouter(prefix="/api", tags=["Tienda"])

@router.get("/products", response_model=list[ProductOut])
def products(db: Session = Depends(get_db)):
    return db.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.id)).all()

@router.get("/products/{product_id}", response_model=ProductOut)
def product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Producto no encontrado.")
    return product

@router.get("/admin/products", response_model=list[ProductOut])
def admin_products(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return db.scalars(select(Product).order_by(Product.id)).all()

def product_values(data: ProductInput):
    values = data.model_dump()
    values["image_url"] = str(data.image_url)
    return values

@router.post("/admin/products", response_model=ProductOut, status_code=201)
def add_product(data: ProductInput, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    product = Product(**product_values(data))
    db.add(product)
    db.flush()
    return product

@router.put("/admin/products/{product_id}", response_model=ProductOut)
def edit_product(product_id: int, data: ProductInput, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    product = db.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        raise HTTPException(404, "Producto no encontrado.")
    for key, value in product_values(data).items():
        setattr(product, key, value)
    db.flush()
    return product

@router.delete("/admin/products/{product_id}", status_code=204)
def deactivate_product(product_id: int, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    product = db.scalar(select(Product).where(Product.id == product_id).with_for_update())
    if not product:
        raise HTTPException(404, "Producto no encontrado.")
    product.is_active = False
    return Response(status_code=204)

def locked_cart(db: Session, user: User) -> Cart:
    db.execute(select(User.id).where(User.id == user.id).with_for_update())
    cart = db.scalar(select(Cart).where(Cart.user_id == user.id))
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
    return cart

def cart_view(cart: Cart):
    items = [{"product": item.product, "quantity": item.quantity, "subtotal": item.product.price * item.quantity} for item in cart.items]
    return {"items": items, "total": sum((i["subtotal"] for i in items), Decimal("0.00"))}

@router.get("/cart", response_model=CartOut)
def get_cart(user: User = Depends(client_user), db: Session = Depends(get_db)):
    return cart_view(locked_cart(db, user))

@router.post("/cart/items", response_model=CartOut)
def add_cart_item(data: CartAddInput, user: User = Depends(client_user), db: Session = Depends(get_db)):
    cart = locked_cart(db, user)
    product = db.get(Product, data.product_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Producto no encontrado.")
    item = next((i for i in cart.items if i.product_id == product.id), None)
    quantity = data.quantity + (item.quantity if item else 0)
    if quantity > product.stock:
        raise HTTPException(409, "No hay stock suficiente.")
    if item:
        item.quantity = quantity
    else:
        cart.items.append(CartItem(product_id=product.id, product=product, quantity=quantity))
    db.flush()
    return cart_view(cart)

@router.patch("/cart/items/{product_id}", response_model=CartOut)
def update_cart_item(product_id: int, data: QuantityInput, user: User = Depends(client_user), db: Session = Depends(get_db)):
    cart = locked_cart(db, user)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(404, "Artículo no encontrado.")
    if not item.product.is_active or data.quantity > item.product.stock:
        raise HTTPException(409, "El producto no está disponible en esa cantidad.")
    item.quantity = data.quantity
    db.flush()
    return cart_view(cart)

@router.delete("/cart/items/{product_id}", status_code=204)
def remove_cart_item(product_id: int, user: User = Depends(client_user), db: Session = Depends(get_db)):
    cart = locked_cart(db, user)
    item = next((i for i in cart.items if i.product_id == product_id), None)
    if not item:
        raise HTTPException(404, "Artículo no encontrado.")
    db.delete(item)
    return Response(status_code=204)

@router.delete("/cart", status_code=204)
def clear_cart(user: User = Depends(client_user), db: Session = Depends(get_db)):
    cart = locked_cart(db, user)
    db.execute(delete(CartItem).where(CartItem.cart_id == cart.id))
    return Response(status_code=204)

@router.post("/orders", response_model=OrderOut, status_code=201)
def checkout(user: User = Depends(client_user), db: Session = Depends(get_db)):
    cart = locked_cart(db, user)
    if not cart.items:
        raise HTTPException(409, "El carrito está vacío.")
    ids = sorted(item.product_id for item in cart.items)
    products = {p.id: p for p in db.scalars(select(Product).where(Product.id.in_(ids)).order_by(Product.id).with_for_update().execution_options(populate_existing=True)).all()}
    for item in cart.items:
        product = products.get(item.product_id)
        if not product or not product.is_active or product.stock < item.quantity:
            raise HTTPException(409, "Algún producto ya no está disponible en la cantidad elegida.")
    order = Order(user_id=user.id, status="pendiente", total=sum((products[i.product_id].price * i.quantity for i in cart.items), Decimal("0.00")))
    for item in cart.items:
        product = products[item.product_id]
        product.stock -= item.quantity
        order.items.append(OrderItem(product_id=product.id, product_name=product.name, unit_price=product.price, quantity=item.quantity))
    db.add(order)
    cart.items.clear()
    db.flush()
    return order

@router.get("/orders", response_model=list[OrderOut])
def orders(user: User = Depends(current_user), db: Session = Depends(get_db)):
    query = select(Order).order_by(Order.id.desc())
    if user.role != "administrador":
        query = query.where(Order.user_id == user.id)
    return db.scalars(query).all()

def find_order(db: Session, order_id: int, user: User, lock=False):
    query = select(Order).where(Order.id == order_id)
    if user.role != "administrador":
        query = query.where(Order.user_id == user.id)
    if lock:
        query = query.with_for_update()
    order = db.scalar(query)
    if not order:
        raise HTTPException(404, "Pedido no encontrado.")
    return order

@router.get("/orders/{order_id}", response_model=OrderOut)
def order_detail(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return find_order(db, order_id, user)

def cancel(db: Session, order: Order):
    if order.status not in {"pendiente", "confirmado", "enviado"}:
        raise HTTPException(409, "Este pedido ya no se puede cancelar.")
    ids = sorted(i.product_id for i in order.items)
    products = {p.id:p for p in db.scalars(select(Product).where(Product.id.in_(ids)).order_by(Product.id).with_for_update().execution_options(populate_existing=True)).all()}
    for item in order.items:
        products[item.product_id].stock += item.quantity
    order.status = "cancelado"
    db.flush()
    return order

@router.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    order = find_order(db, order_id, user, lock=True)
    if user.role != "administrador" and order.status != "pendiente":
        raise HTTPException(409, "Solo puedes cancelar pedidos pendientes.")
    return cancel(db, order)

@router.patch("/admin/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, data: OrderStatusInput, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    order = find_order(db, order_id, user, lock=True)
    allowed = {"pendiente":{"confirmado", "cancelado"}, "confirmado":{"enviado", "cancelado"}, "enviado":{"entregado", "cancelado"}}
    if data.status not in allowed.get(order.status, set()):
        raise HTTPException(409, "La transición de estado no está permitida.")
    if data.status == "cancelado":
        return cancel(db, order)
    order.status = data.status
    db.flush()
    return order
