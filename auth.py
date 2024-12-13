import bcrypt  # Библиотека для хэширования
from database import session, User

# Функция для хэширования пароля
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Функция для проверки пароля
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Авторизация пользователя
def login_user(username, password):
    user = session.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.password):  # Проверяем пароль с хэшем
        return "Ошибка: Неверное имя пользователя или пароль.", None
    return f"Добро пожаловать, {username}!", user.id

# Регистрация пользователя
def register_user(username, password, role="user"):
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        return "Ошибка: Пользователь с таким именем уже существует."
    
    hashed_password = hash_password(password)  # Хэшируем пароль перед сохранением
    new_user = User(username=username, password=hashed_password, role=role)
    session.add(new_user)
    session.commit()
    return "Регистрация прошла успешно!"

# Проверка роли пользователя
def check_user_role(username):
    user = session.query(User).filter_by(username=username).first()
    return user.role if user else None