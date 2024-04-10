from fastapi import FastAPI

from routers.produto_routes import router as produto_router
from routers.setor_routes import router as setor_router
from routers.usuario_routes import router as usuario_router
#from routers import produto_routes, setor_routes, usuario_routes

# Instanciando app
app = FastAPI()

# método get pelo endpoint /


@app.get('/health-check')
def checar():
    return "api funcionando!"

app.include_router(produto_router)
app.include_router(setor_router)
app.include_router(usuario_router)

#@app.get('/health-check') 
# def health_check():
#    return "api no ar"
#    return True
app.include_router(setor_router, tags=['setores'])
#app.include_router(produto_router)
#app.include_router(usuario_router)

#app.include_router(produto_router.router, tags=['produtos'])
app.include_router(setor_routes.router, tags=['setores'])
#app.include_router(usuario_routes.router, tags=['usuarios'])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)