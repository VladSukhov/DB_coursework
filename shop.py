from database import session, Batch, Order

# Получить список всех товаров
def get_all_products():
    products = session.query(Batch).all()
    return [{"id": product.id, "name": product.name, "description": product.description, "price": product.price}
            for product in products]

# Создать заказ
def create_order(user_id, batch_id):
    batch = session.query(Batch).filter_by(id=batch_id).first()
    if not batch:
        return "Ошибка: Партия с таким ID не найдена."
    
    if batch.quantity <= 0:
        return "Ошибка: Партия закончилась."
    
    new_order = Order(user_id=user_id, batch_id=batch_id, status="pending")
    session.add(new_order)
    session.commit()
    return f"Заказ успешно создан. ID заказа: {new_order.id}"

# Просмотр заказов
def view_orders(user_id=None, is_admin=False):
    if is_admin:
        orders = session.query(Order).all()
    else:
        orders = session.query(Order).filter_by(user_id=user_id).all()
    
    return [
        {"id": order.id, "user_id": order.user_id, "batch_id": order.batch_id,
         "status": order.status}
        for order in orders
    ]

# Обновление статуса заказа (для администратора)
def update_order_status(order_id, new_status):
    order = session.query(Order).filter_by(id=order_id).first()
    if not order:
        return "Ошибка: Заказ не найден."
    
    order.status = new_status
    session.commit()
    return f"Статус заказа {order_id} обновлен на '{new_status}'."