import streamlit as st
from sqlalchemy.orm import sessionmaker
from database import engine, session, User, Batch, Order, Supplier, Saler
import random

Session = sessionmaker(bind=engine)
session = Session()

# Инициализация состояния
def init_session_state():
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "selected_products" not in st.session_state:
        st.session_state.selected_products = {}

# Функция для входа
def login_user(username, password):
    user = session.query(User).filter_by(username=username, password=password).first()
    if user:
        st.session_state.is_authenticated = True
        st.session_state.current_user = user
        st.success(f"Добро пожаловать, {user.username}!")
    else:
        st.error("Неверное имя пользователя или пароль.")

# Функция для отображения текущего состояния заказа
def display_selected_products():
    st.subheader("Текущий заказ")
    selected_products = st.session_state.selected_products
    if not any(quantity > 0 for quantity in selected_products.values()):
        st.info("Вы пока не выбрали ни одного продукта.")
        return

    for batch_id, quantity in selected_products.items():
        if quantity > 0:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            st.text(f"{batch.name}: {quantity} шт.")

# Функция для просмотра заказов текущего пользователя
def view_user_orders():
    st.subheader("Мои заказы")

    if not st.session_state.is_authenticated or not st.session_state.current_user:
        st.error("Пожалуйста, войдите в систему, чтобы просмотреть свои заказы.")
        return

    # Получаем заказы текущего пользователя, сгруппированные по номеру партии
    user_orders = (
        session.query(Order)
        .filter_by(user_id=st.session_state.current_user.id)
        .order_by(Order.batch_number)
        .all()
    )

    if not user_orders:
        st.info("У вас пока нет заказов.")
        return

    # Группируем заказы по batch_number
    grouped_orders = {}
    for order in user_orders:
        if order.batch_number not in grouped_orders:
            grouped_orders[order.batch_number] = []
        grouped_orders[order.batch_number].append(order)

    # Отображаем заказы по группам
    for batch_number, orders in grouped_orders.items():
        st.markdown(f"### Партия № {batch_number}")
        supplier_name = session.query(Supplier).filter_by(id=orders[0].supplier_id).first().name
        saler_name = session.query(Saler).filter_by(id=orders[0].saler_id).first().name

        st.write(f"**Поставщик:** {supplier_name}")
        st.write(f"**Магазин-продавец:** {saler_name}")
        st.write(f"**Статус партии:** {orders[0].status}")

        st.markdown("#### Состав партии:")
        for order in orders:
            product = session.query(Batch).filter_by(id=order.batch_id).first()
            st.write(f"- {product.name} (Количество: {order.quantity})")

        st.markdown("---")

# Функция для просмотра всех заказов (только для админа)
def view_all_orders():
    st.subheader("Все заказы (для администратора)")

    # Проверка на права доступа
    if not st.session_state.is_authenticated or st.session_state.current_user.role != "admin":
        st.error("У вас нет доступа к этому разделу.")
        return

    # Получаем все заказы
    all_orders = session.query(Order).all()

    if not all_orders:
        st.info("Заказы отсутствуют.")
        return

    # Группируем заказы по номерам партии
    orders_by_batch = {}
    for order in all_orders:
        if order.batch_number not in orders_by_batch:
            orders_by_batch[order.batch_number] = []
        orders_by_batch[order.batch_number].append(order)

    # Отображение и управление партиями
    for batch_number, orders in orders_by_batch.items():
        st.write(f"**Номер партии:** {batch_number}")
        
        # Отображение заказов в партии
        for order in orders:
            user = session.query(User).filter_by(id=order.user_id).first()
            batch = session.query(Batch).filter_by(id=order.batch_id).first()
            st.write(f"- Пользователь: {user.username}")
            st.write(f"  Продукт: {batch.name}")
            st.write(f"  Количество: {order.quantity}")
            st.write(f"  Текущий статус: {order.status}")

        # Проверка текущего статуса партии
        current_status = orders[0].status
        st.write(f"**Текущий статус партии:** {current_status}")

        # Изменение статуса всей партии
        new_status = st.selectbox(
            f"Изменить статус партии {batch_number}",
            options=["pending", "approved", "rejected"],
            index=["pending", "approved", "rejected"].index(current_status),
            key=f"batch_status_{batch_number}"
        )

        if st.button(f"Обновить статус партии {batch_number}", key=f"update_batch_{batch_number}"):
            for order in orders:
                order.status = new_status
            session.commit()
            st.success(f"Статус партии {batch_number} изменен на {new_status}.")

        # Удаление партии
        if st.button(f"Удалить партию {batch_number}", key=f"delete_batch_{batch_number}"):
            # Удаляем все заказы с этим номером партии
            session.query(Order).filter_by(batch_number=batch_number).delete()
            session.commit()
            st.success(f"Партия {batch_number} успешно удалена.")
            # Обновляем сессию
            st.session_state["refresh"] = not st.session_state.get("refresh", False)

        st.markdown("---")

# Инициализация состояния сессии
def init_session_state():
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "selected_products" not in st.session_state:
        st.session_state.selected_products = {}
    if "selected_supplier" not in st.session_state:
        st.session_state.selected_supplier = None
    if "selected_saler" not in st.session_state:
        st.session_state.selected_saler = None

# Функция для создания нового заказа
def create_order():
    st.subheader("Создание нового заказа")

    if not st.session_state.is_authenticated or not st.session_state.current_user:
        st.error("Пожалуйста, войдите в систему, чтобы создать заказ.")
        return

    batches = session.query(Batch).all()
    suppliers = session.query(Supplier).all()
    salers = session.query(Saler).all()

    if not batches:
        st.warning("Нет доступных продуктов для заказа.")
        return
    if not suppliers:
        st.warning("Нет доступных поставщиков.")
        return
    if not salers:
        st.warning("Нет доступных магазинов-продавцов.")
        return

    # Выбор продуктов
    st.write("**Выберите продукты и их количество:**")
    for batch in batches:
        col1, col2 = st.columns(2)
        with col1:
            st.text(f"{batch.name} ({batch.description})")
            st.text(f"Цена: {batch.price} руб.")
            st.text(f"Доступно: {batch.quantity}")
        with col2:
            if batch.id not in st.session_state.selected_products:
                st.session_state.selected_products[batch.id] = 0

            quantity = st.number_input(
                f"Количество для {batch.name}",
                min_value=0,
                max_value=batch.quantity,
                value=st.session_state.selected_products[batch.id],
                step=1,
                key=f"batch_{batch.id}",
            )
            st.session_state.selected_products[batch.id] = quantity

    # Выбор поставщика
    st.write("**Выберите поставщика для доставки заказа:**")
    supplier_options = {supplier.id: supplier.name for supplier in suppliers}
    selected_supplier_id = st.selectbox(
        "Поставщик", options=list(supplier_options.keys()), format_func=lambda x: supplier_options[x]
    )
    st.session_state.selected_supplier = selected_supplier_id

    # Выбор магазина-продавца
    st.write("**Выберите магазин-продавца для доставки заказа:**")
    saler_options = {saler.id: saler.name for saler in salers}
    selected_saler_id = st.selectbox(
        "Магазин-продавец", options=list(saler_options.keys()), format_func=lambda x: saler_options[x]
    )
    st.session_state.selected_saler = selected_saler_id

    if st.button("Оформить заказ"):
        batch_number = submit_order()
        if batch_number:
            st.success(f"Заказ успешно оформлен! Номер заказа: {batch_number}")

# Функция для оформления заказа
def submit_order():
    selected_products = st.session_state.selected_products
    selected_supplier = st.session_state.selected_supplier
    selected_saler = st.session_state.selected_saler

    if not any(quantity > 0 for quantity in selected_products.values()):
        st.warning("Выберите хотя бы один продукт.")
        return None

    if not selected_supplier:
        st.warning("Выберите поставщика.")
        return None

    if not selected_saler:
        st.warning("Выберите магазин-продавца.")
        return None

    # Создание заказа
    batch_number = random.randint(1, 9999)
    order_id = None
    for batch_id, quantity in selected_products.items():
        if quantity > 0:
            batch = session.query(Batch).filter_by(id=batch_id).first()
            if batch.quantity < quantity:
                st.error(f"Недостаточно {batch.name} на складе!")
                continue

            batch.quantity -= quantity
            order = Order(
                user_id=st.session_state.current_user.id,
                batch_id=batch_id,
                quantity=quantity,
                status="pending",
                batch_number=batch.id,
                supplier_id=selected_supplier,
                saler_id=selected_saler,
            )
            session.add(order)          

    session.commit()
    st.session_state.selected_products = {}
    return batch_number

# Главная функция приложения
def main():
    st.title("Milk Factory Service")

    init_session_state()

    if not st.session_state.is_authenticated:
        choice = st.sidebar.selectbox("Действие", ["Войти", "Регистрация"])
    else:
        if st.session_state.current_user.role == "user":
            choice = st.sidebar.selectbox("Действие", ["Создать заказ", "Мои заказы", "Выйти"])
        elif st.session_state.current_user.role == "admin":
            choice = st.sidebar.selectbox("Действие", ["Просмотреть заказы", "Выйти"])

    if choice == "Войти":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        if st.button("Войти"):
            login_user(username, password)
    elif choice == "Регистрация":
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        role = st.selectbox("Роль", ["user", "admin"])
        if st.button("Зарегистрироваться"):
            if session.query(User).filter_by(username=username).first():
                st.warning("Имя пользователя уже занято.")
            else:
                new_user = User(username=username, password=password, role=role)
                session.add(new_user)
                session.commit()
                st.success("Регистрация прошла успешно!")
    elif choice == "Создать заказ":
        create_order()
    elif choice == "Мои заказы":
        view_user_orders()
    elif choice == "Просмотреть заказы":
        view_all_orders()
    elif choice == "Выйти":
        st.session_state.is_authenticated = False
        st.session_state.current_user = None
        st.success("Вы вышли из системы.")

if __name__ == "__main__":
    main()