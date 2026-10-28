from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="API Controle de Estoque",
    description="API para controle de estoque de produtos",
)

# lista de dados pra ser o banco de dados, contador de IDs
lista_de_dados = []
contador_id = 1

class Produto(BaseModel):
    nome: str
    quantidade: int
    preco: float
    
class ProdutoResponse(Produto):
    id: int
    
# endpoints

@app.post("/produtos/", response_model=ProdutoResponse)
def criar_produto(produto: Produto):
    global contador_id
    novo_produto = produto.model_dump()
    novo_produto["id"] = contador_id
    
    lista_de_dados.append(novo_produto)
    contador_id += 1
    
    return novo_produto

@app.get("/produtos/", response_model=List[ProdutoResponse])
def listar_produtos(limite: int = 10):
    return lista_de_dados[:limite]

@app.get("/produtos/{produto_id}", response_model=ProdutoResponse)
def obter_produto(produto_id: int):
    for produto in lista_de_dados:
        if produto["id"] == produto_id:
            return produto
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.put("/produtos/{produto_id}", response_model=ProdutoResponse)
def atualizar_produto(produto_id: int, produto_atualizado: Produto):
    for produto in lista_de_dados:
        if produto["id"] == produto_id:
            produto.update(produto_atualizado.model_dump())
            return produto
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.delete("/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    for index, produto in enumerate(lista_de_dados):
        if produto["id"] == produto_id:
            del lista_de_dados[index]
            return 
    raise HTTPException(status_code=404, detail="Produto não encontrado")