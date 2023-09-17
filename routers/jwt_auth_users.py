from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models.userBasicAuth import UserBA
from models.userDB import UserDB

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1
SECRET = "29c444e3b262b8c0fff38ec064c3292049817075f30119775f36ee746a219744"

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="loginjwt")

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")#Los schemes definen el algoritmo de encriptacion utilizado

users_db = {
    "ricardo": {
        "username": "ricardo",
        "full_name": "Ricardo Electrico",
        "email": "RE@email.com",
        "disabled": False,
        "password": "$2a$12$xWJkmqVc.TwyfbiNwZn4kOytg4gcO4R3Jmxwy9WtbqOxzgH2gmoFa"#asd
    },
    "carlos": {
        "username": "carlos",
        "full_name": "Carlos Electrico",
        "email": "CE@email.com",
        "disabled": True,
        "password": "$2a$12$fnakuqztLnU3XW1OkJ5IJ.1.f8lq7x9U0kN1FzT0cCemG3B1NYJvC"#123
    }
}

def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return UserBA(**users_db[username])

async def auth_user(token: str = Depends(oauth2)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticacion invalidas",
        headers={"WWW-Authenticate": "Bearer"})
    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return search_user(username)
    
#criterio de dependencia
async def current_user(user: UserBA = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo")
    return user

@router.post("/loginjwt")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if not users_db.get(form.username):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="El usuario no es correcto")
    user = search_user_db(form.username)

    if not crypt_context.verify(form.password, user.password):
        #Verifica que la contraseña enviada desde un formulario matchee con la encriptada guardada en base de datos.
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail="La contraseña no es correcta")
    
    access_token = {"sub": user.username,#Nombre de usuario
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)#cuando expira el token
                    }

    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/usersjwt/me")
async def me(user: UserBA = Depends(current_user)):
    return user