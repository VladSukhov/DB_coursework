from database import session, User, Product, Batch, Order
import datetime

def seed_data():
    # Очистка данных перед добавлением
    session.query(Order).delete()
    session.query(Batch).delete()
    session.query(Product).delete()
    session.query(User).delete()

    # Создание пользователей
    admin = User(username="admin", password_hash="admin123", role="admin")
    user = User(username="user", password_hash="user123", role="user")
    
    session.add_all([admin, user])

    # Создание товаров
    milk = Product(name="Молоко", description="1 литр пастеризованного молока", price=1.2, composition="Молоко")
    cheese = Product(name="Сыр", description="500 грамм твердого сыра", price=5.5, composition="Молоко, соль, ферменты")
    
    session.add_all([milk, cheese])

    # Создание партий
    batch1 = Batch(product_id=1, quantity=100, production_date=datetime.datetime(2024, 1, 1))
    batch2 = Batch(product_id=2, quantity=50, production_date=datetime.datetime(2024, 1, 2))

    session.add_all([batch1, batch2])

    # Создание заказов
    order1 = Order(user_id=2, batch_id=1, status="pending")
    order2 = Order(user_id=2, batch_id=2, status="approved")
    
    session.add_all([order1, order2])

    # Сохранение изменений
    session.commit()
    print("База данных успешно заполнена тестовыми данными!")

if __name__ == "__main__":
    seed_data()