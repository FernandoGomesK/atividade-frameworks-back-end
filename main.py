from fastapi import FastAPI
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