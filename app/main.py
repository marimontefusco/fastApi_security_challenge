from fastapi import FastAPI
from routers.produto_routes import router as produto_router
from routers.setor_routes import router as setor_router
from routers.usuario_routes import router as usuario_router

# Instanciando app
app = FastAPI()

# método get pelo endpoint 
@app.get('/health-check')
def checar():
    print("api funcionando!")
    return True

# incluindo os routers
app.include_router(produto_router, tags=['produtos'])
app.include_router(setor_router, tags=['setores'])
app.include_router(usuario_router, tags=['usuarios'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)