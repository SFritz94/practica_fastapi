from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import products, users, basic_auth_users, jwt_auth_users

app = FastAPI()

#Routers
app.include_router(products.router)#Forma de cargar las diferentes rutas en la api
app.include_router(users.router)

app.include_router(basic_auth_users.router)
app.include_router(jwt_auth_users.router)

app.mount("/static", StaticFiles(directory="static"), name="static")#Forma de cargar recursos estaticos (pathcon el q se accede por navegador, directorio, nombre)

@app.get("/")
async def root():
    return { "message": "Hello World" }

#Inicia el server: uvicorn main:app --reload