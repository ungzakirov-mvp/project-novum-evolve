import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Используем SQLite в памяти для быстрых тестов
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """
    Фикстура базы данных.
    Создает таблицы перед каждым тестом и удаляет после.
    """
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    
    # Seed Test Data
    from app.models import Tenant, TicketStatus
    tenant = Tenant(name="Test Company", slug="demo", domain="test.local")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    
    status = TicketStatus(tenant_id=tenant.id, name="New", color="blue", order=1)
    db_session.add(status)
    db_session.commit()
    
    try:
        yield db_session
    finally:
        db_session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """
    Фикстура клиента FastAPI.
    Переопределяет зависимость get_db.
    """
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
