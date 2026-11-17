from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from sqlalchemy.orm import Session

from database import get_db
from models import ProdutoDB, UsuarioDB

from auth import gerar_senha_hash, verificar_senha, criar_token_acesso, validar_usuario


app = FastAPI(
    title="API Controle de Estoque",
    description="API para controle de estoque de produtos",
)

class UsuarioCreate(BaseModel):
    email: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Produto(BaseModel):
    nome: str
    quantidade: int
    preco: float
    
class ProdutoResponse(Produto):
    id: int

    class Config:
        from_attributes = True
    
# endpoints

@app.post("/usuarios/",
          summary="Criar usuário",
          tags=["Usuários"])
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário no banco de dados.
    """
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = UsuarioDB(email=usuario.email, senha=gerar_senha_hash(usuario.senha))
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"detail": "Usuário criado com sucesso"}

@app.post("/token",
          summary="Login",
          tags=["Autenticação"],
          response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Realiza o login do usuário e retorna um token de acesso.
    """
    usuario = db.query(UsuarioDB).filter(UsuarioDB.email == form_data.username).first()
    
    if not usuario or not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    token = criar_token_acesso(data={"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}


# Endpoints de produtos


@app.post("/produtos/",
          summary="Criar produto",
          tags=["Produtos"],
          response_model=ProdutoResponse)
def criar_produto(produto: Produto, db: Session = Depends(get_db),
                  usuario_atual: UsuarioDB = Depends(validar_usuario)):
    """
    Cria um novo produto no banco de dados.
    """

    produto_existente = db.query(ProdutoDB).filter(ProdutoDB.nome == produto.nome).first()
    if produto_existente:
        raise HTTPException(status_code=400, detail="Produto já existe")

    novo_produto = ProdutoDB(**produto.model_dump())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    
    return novo_produto

@app.get("/produtos/",
         summary="Listar produtos",
         tags=["Produtos"],
         response_model=List[ProdutoResponse])
def listar_produtos(limite: int = 10, db:Session = Depends(get_db)):
    """
    Retorna uma lista de produtos com um limite específico.
    """
    produtos = db.query(ProdutoDB).limit(limite).all()
    return produtos

@app.get("/produtos/{produto_id}", 
         summary="Obter produto",
         tags=["Produtos"],
         response_model=ProdutoResponse)
         
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """
    Retorna os detalhes de um produto específico.
    """
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.put("/produtos/{produto_id}", 
         summary="Atualizar produto",
        tags=["Produtos"],
         response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, produto_atualizado: Produto, db: Session = Depends(get_db),
                      usuario_logado: UsuarioDB = Depends(validar_usuario)):
    """
    Atualiza os dados de um produto específico.
    """
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for key, value in produto_atualizado.model_dump().items():
        setattr(produto, key, value)

    db.commit()
    db.refresh(produto)
    return produto

@app.delete("/produtos/{produto_id}", 
            summary="Deletar produto",
            tags=["Produtos"],
            status_code=204)
def deletar_produto(produto_id: int, db: Session = Depends(get_db), 
                    usuario_logado: UsuarioDB = Depends(validar_usuario)):
    """
    Remove um produto específico.
    """
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return 
