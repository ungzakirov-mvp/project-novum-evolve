def test_register_user(client):
    """Тест успешной регистрации пользователя"""
    response = client.post("/api/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    """Тест регистрации с существующим email"""
    # Создаем первого пользователя
    client.post("/api/auth/register", json={
        "email": "duplicate@test.com",
        "password": "password123",
        "full_name": "First User"
    })
    
    # Пытаемся создать второго с тем же email
    response = client.post("/api/auth/register", json={
        "email": "duplicate@test.com",
        "password": "password456",
        "full_name": "Second User"
    })
    assert response.status_code == 400
    assert "уже существует" in response.json()["detail"]


def test_login_user(client):
    """Тест успешного входа"""
    # Регистрируем пользователя
    client.post("/api/auth/register", json={
        "email": "login@test.com",
        "password": "password123",
        "full_name": "Login User"
    })
    
    # Выполняем вход
    response = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_invalid_credentials(client):
    """Тест входа с неверным паролем"""
    # Регистрируем пользователя
    client.post("/api/auth/register", json={
        "email": "wrong@test.com",
        "password": "password123"
    })
    
    # Пытаемся войти с неверным паролем
    response = client.post("/api/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
