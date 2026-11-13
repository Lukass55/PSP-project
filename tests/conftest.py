import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def create_account(client):
    def _create_account(
        username="lukas",
        name="Lukas",
        surname="Test",
        password="Test12345"
    ):
        response = client.post(
            "/auth/register",
            json={
                "username": username,
                "name": name,
                "surname": surname,
                "password": password
            }
        )

        assert response.status_code == 201, response.text

        login = client.post(
            "/auth/login",
            json={
                "username": username,
                "password": password
            }
        )

        assert login.status_code == 200, login.text

        me = client.get("/auth/me")
        assert me.status_code == 200

        return me.json()

    return _create_account


@pytest.fixture
def create_group(client, create_account):
    def _create_group():
        account = create_account()

        members = []

        for name in ["Tomas", "Matas"]:
            response = client.post(
                "/users",
                json={
                    "name": name,
                    "surname": "Test"
                }
            )

            assert response.status_code == 201, response.text
            members.append(response.json()["id"])

        response = client.post(
            "/groups",
            json={
                "name": "Kelionė",
                "member_ids": members
            }
        )

        assert response.status_code == 201, response.text

        return {
            "account": account,
            "group_id": response.json()["id"],
            "user_ids": [account["user_id"], *members]
        }

    return _create_group
