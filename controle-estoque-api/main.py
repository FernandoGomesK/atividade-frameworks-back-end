from typing import List

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session

from database import get_db
from models import ProdutoDB


app = FastAPI(
    title="API Controle de Estoque",
    description="API para controle de estoque de produtos",
)

# lista de dados pra ser o banco de dados, contador de IDs

# lista_de_dados = []
# contador_id = 1

class Produto(BaseModel):
    nome: str
    quantidade: int
    preco: float
    
class ProdutoResponse(Produto):
    id: int

    class Config:
        from_attributes = True
    
# endpoints

@app.post("/produtos/", response_model=ProdutoResponse)
def criar_produto(produto: Produto, db: Session = Depends(get_db)):
    # global contador_id
    # novo_produto = produto.model_dump()
    # novo_produto["id"] = contador_id
    
    # lista_de_dados.append(novo_produto)
    # contador_id += 1

    produto_existente = db.query(ProdutoDB).filter(ProdutoDB.nome == produto.nome).first()
    if produto_existente:
        raise HTTPException(status_code=400, detail="Produto já existe")

    novo_produto = ProdutoDB(**produto.model_dump())
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    
    return novo_produto

@app.get("/produtos/", response_model=List[ProdutoResponse])
def listar_produtos(limite: int = 10, db:Session = Depends(get_db)):
    produtos = db.query(ProdutoDB).limit(limite).all()
    return produtos

@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto

@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, produto_atualizado: Produto, db: Session = Depends(get_db)):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    for key, value in produto_atualizado.model_dump().items():
        setattr(produto, key, value)

    db.commit()
    db.refresh(produto)
    return produto

@app.delete("/produtos/{produto_id}", status_code=204)
def deletar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(ProdutoDB).filter(ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return 
