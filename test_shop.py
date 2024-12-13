from shop import get_all_products, create_order, view_orders, update_order_status

if __name__ == "__main__":
    # Просмотр всех товаров
    products = get_all_products()
    print("Список товаров:")
    for product in products:
        print(product)

    # Создание заказа
    print(create_order(user_id=2, batch_id=1))  # Пользователь делает заказ
    
    # Просмотр заказов (как пользователь)
    print("Мои заказы:")
    user_orders = view_orders(user_id=2)
    for order in user_orders:
        print(order)
    
    # Просмотр заказов (как администратор)
    print("Все заказы (админ):")
    admin_orders = view_orders(is_admin=True)
    for order in admin_orders:
        print(order)

    # Изменение статуса заказа
    print(update_order_status(order_id=1, new_status="approved"))