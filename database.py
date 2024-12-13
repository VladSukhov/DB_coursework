from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Базовый класс для декларативной ORM
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")

    orders = relationship("Order", back_populates="user")

# Модель партии продуктов
class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    orders = relationship("Order", back_populates="batch")

# Модель заказов
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    quantity = Column(Integer, nullable=False)  # Количество продукта в заказе
    status = Column(String, nullable=False, default="pending")
    batch_number = Column(Integer, nullable=False)  # Номер партии
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    saler_id = Column(Integer, ForeignKey('salers.id'))

    user = relationship("User", back_populates="orders")
    batch = relationship("Batch", back_populates="orders")

# Модель журнала действий (Logs)
class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    action = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    user = relationship("User")

# Модель поставщиков (Suppliers)
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

# Модель магазинов-продавцов (Salers)
class Saler(Base):
    __tablename__ = "salers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

# Модель продаж (Sales)
class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    saler_id = Column(Integer, ForeignKey("salers.id"), nullable=False)
    timestamp = Column(String, nullable=False)

    batch = relationship("Batch")
    saler = relationship("Saler")

# Создание движка и сессии
engine = create_engine("sqlite:///milk_factory.db")
Session = sessionmaker(bind=engine)
session = Session()

# Создание таблиц и добавление данных
if __name__ == "__main__":
    Base.metadata.create_all(engine)

    # Добавление начальных продуктов
    initial_batches = [
        Batch(name="Молоко 1 литр", description="Свежий продукт", price=50, quantity=100),
        Batch(name="Кефир 1 литр", description="Натуральный кефир", price=60, quantity=80),
        Batch(name="Сметана 500 грамм", description="Сметана 15%", price=70, quantity=50),
        Batch(name="Йогурт 250 грамм", description="Йогурт с клубникой", price=40, quantity=120),
        Batch(name="Творог 200 грамм", description="Творог 9%", price=80, quantity=60),
        Batch(name="Масло сливочное 200 грамм", description="Масло 82%", price=150, quantity=30),
        Batch(name="Сыр твердый 1 кг", description="Сыр Гауда", price=400, quantity=20),
        Batch(name="Сливки 200 мл", description="Сливки 20%", price=90, quantity=40),
        Batch(name="Ряженка 500 мл", description="Домашняя ряженка", price=70, quantity=100),
        Batch(name="Йогурт 500 грамм", description="Натуральный йогурт", price=90, quantity=50),
    ]

        # Добавление начальных поставщиков
    suppliers = [
        Supplier(name="ООО Молочная Ферма", address="г. Москва, ул. Ленина, 15"),
        Supplier(name="ИП Коровкин", address="г. Санкт-Петербург, ул. Молочная, 20"),
        Supplier(name="Молочный завод 'Свежее'", address="г. Казань, пр. Победы, 10"),
        Supplier(name="ЗАО Фермер", address="г. Новосибирск, ул. Полевая, 5"),
        Supplier(name="Агрокомплекс 'Деревенька'", address="г. Екатеринбург, ул. Центральная, 8"),
    ]

    # Добавление начальных магазинов-продавцов
    salers = [
        Saler(name="Магазин 'Молочная радость'", address="г. Москва, ул. Тверская, 22"),
        Saler(name="Сеть магазинов 'Продукты рядом'", address="г. Санкт-Петербург, ул. Ладожская, 30"),
        Saler(name="Супермаркет 'Еда для всех'", address="г. Казань, ул. Университетская, 12"),
        Saler(name="Гипермаркет 'Всё вкусное'", address="г. Новосибирск, пр. Мира, 45"),
        Saler(name="Магазин 'Продукты от фермеров'", address="г. Екатеринбург, ул. Кирова, 18"),
    ]

    session.add_all(suppliers)
    session.add_all(salers)
    session.add_all(initial_batches)
    session.commit()
    print("Начальные продукты добавлены.")