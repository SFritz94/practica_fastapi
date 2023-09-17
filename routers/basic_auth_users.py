from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.userBasicAuth import UserBA
from models.userDB import UserDB

#OAuth2PasswordBearer -> Clase que se encarga de gestionar la autenticacion
#OAuth2PasswordRequestForm -> Forma en la que se envia a nuestra api los criterios de autenticacion. Forma de capturar user y pass

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")#/login

users_db = {
    "ricardo": {
        "username": "ricardo",
        "full_name": "Ricardo Electrico",
        "email": "RE@email.com",
        "disabled": False,
        "password": "asd"
    },
    "carlos": {
        "username": "carlos",
        "full_name": "Carlos Electrico",
        "email": "CE@email.com",
        "disabled": True,
        "password": "123"
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return UserBA(**users_db[username])

#criterio de dependencia
async def current_user(token: str = Depends(oauth2)):
    user =  search_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticacion invalidas",
            headers={"WWW-Authenticate": "Bearer"})
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")
    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if not users_db.get(form.username):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es correcto")
    user = search_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="La contraseña no es correcta")
    return {"access_token": user.username, "token_type": "bearer"}

@router.get("/users/me")
async def me(user: UserBA = Depends(current_user)):
    return user