# Projeto de FAST API Controle de Estoque

O Projeto contido neste arquivo se trata de um controle de Estoque, empregando e utilizando as funções do CRUD

## Integrantes

- Fernando Gomes dos Santos

## Como rodar localmente

- Faça o download dos arquivos
- Instale o Python
- No terminal, acesse a pasta interna com o comando: cd controle-estoque-api
- Instale as dependências com o comando: `pip install -r requirements.txt`
- Crie o banco de dados e as tabelas com o comando: alembic upgrade head
- Execute com o comando: uvicorn main:app --reload através do terminal
- Abra a documentação no navegador: http://127.0.0.1:8000/docs

## Autenticação
Pra utilizar as rotas de produto é necessário criar um usuario com email e senha. 
Depois de realizar o login (você pode usar o botão "Authorize" no topo do Swagger), o sistema devolve um token JWT que precisa ser inserido quando for realizar uma das operações CRUD.

## Como rodar os testes
Dentro da pasta `controle-estoque-api`, execute no terminal:
- `pytest`
