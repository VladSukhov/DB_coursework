from auth import register_user, login_user, check_user_role

if __name__ == "__main__":
    # Тест регистрации
    print(register_user("admin2", "password123", "admin"))
    print(register_user("user2", "password123", "user"))
    
    # Тест входа
    print(login_user("admin2", "password123"))
    print(login_user("user2", "wrongpassword"))
    
    # Проверка роли
    print(check_user_role("admin2"))
    print(check_user_role("unknown_user"))