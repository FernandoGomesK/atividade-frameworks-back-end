import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



@pytest.fixture(autouse=True)
def preparar_banco():
    """
    Prepara o banco de dados para os testes, criando as tabelas antes de cada teste e removendo-as depois.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)



def override_get_db():
    """
    Sobrescreve a função get_db para usar o banco de dados de teste.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Testes

def test_listar_produtos():
    """
    Testa o endpoint da listagem de produtos, se ele retorna um código 200, e uma lista vazia
    """
    response = client.get("/produtos/")
    assert response.status_code == 200
    assert response.json() == []


def test_obter_produto_inexistente():
    """
    Testa o endpoint de obtenção de um produto inexistente, se ele retorna um código 404 e a mensagem correta.
    """
    response = client.get("/produtos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Produto não encontrado"


def test_criar_produto_sem_token():
    """
    Testa o endpoint de criação de produto sem token, se ele retorna um código 401.
    """
    response = client.post(
        "/produtos/",
        json={"nome": "Teclado Mecânico", "quantidade": 5, "preco": 250.0}
    )
    assert response.status_code == 401


def test_criar_usuario_e_login():
    """
    Testa a criação de um usuário e o login subsequente, verificando se o token de acesso é retornado corretamente."""
    res_cadastro = client.post(
        "/usuarios/",
        json={"email": "teste@email.com", "senha": "123"}
    )
    assert res_cadastro.status_code == 200

    res_login = client.post(
        "/token",
        data={"username": "teste@email.com", "password": "123"}
    )
    assert res_login.status_code == 200
    assert "access_token" in res_login.json()
    assert res_login.json()["token_type"] == "bearer"


def test_criar_produto_autenticado():
    """
    Cria um usuário, faz o login e cria um produto pra verificar se a rota ta funcionando
    """
    client.post("/usuarios/", json={"email": "admin@email.com", "senha": "123"})
    res_login = client.post("/token", data={"username": "admin@email.com", "password": "123"})
    token = res_login.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/produtos/",
        json={"nome": "Mouse Sem Fio", "quantidade": 12, "preco": 95.50},
        headers=headers
    )
    
    assert response.status_code == 200
    dados = response.json()
    assert dados["nome"] == "Mouse Sem Fio"
    assert dados["quantidade"] == 12
    assert "id" in dados