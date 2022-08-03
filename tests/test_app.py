import pytest
from app.db_models import db
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"
    app.config["WTF_CSRF_ENABLED"] = False

    context = app.app_context()
    context.push()

    db.create_all()

    yield app.test_client()

    db.session.remove()
    db.drop_all()
    
    context.pop()



def test_se_a_pagina_de_usuarios_retorna_status_code_200(client):
    response = client.get("/")
    assert response.status_code == 200

def test_se_o_link_de_resgistrar_existe(client):
    response = client.get("/")
    assert "register" in response.get_data(as_text=True)

def test_se_o_link_de_login_existe(client):
    response = client.get("/")
    assert "login" in response.get_data(as_text=True)

def test_registrando_usuario(client):
    data = {
        "name": "Amanda",
        "phone": "5529928826",
        "email": "amanda@spacedevs.com.br",
        "password": "12345678wasd",
        "confirm": "12345678wasd",
        "admin": "y"
    }
    response = client.post("/register", data=data, follow_redirects=True)
    assert "login" in response.get_data(as_text=True)

def test_logando_usuario(client):
    data = {        
        "email": "amanda@spacedevs.com.br",
        "password": "12345678wasd"
    }
    client.post("/register", data=data, follow_redirects=True)
    response = client.post("/login", data=data, follow_redirects=True)
    assert "" in response.get_data(as_text=True)