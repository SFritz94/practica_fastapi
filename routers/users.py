from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from bson import ObjectId, errors as bson_errors
from db.models.user import User
from db.schemas.user import user_schema, users_schema
from db.client import db_client

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "message": "Usuario no encontrado"
        },
        status.HTTP_409_CONFLICT:{
            "message": "Usuario ya existente"
        }
    }
)

@router.get("/all", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

# Parametros por Path
@router.get("/{id}", response_model=User)
async def user(id: str):
    try:
        user = search_user("_id", ObjectId(id))
        return user if user else JSONResponse(content=router.responses[status.HTTP_404_NOT_FOUND],status_code=status.HTTP_404_NOT_FOUND)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID no válido")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

# Parametros por Query - http://127.0.0.1:8000/user/?id=4 - http://127.0.0.1:8000/user?id=4
@router.get("/", response_model=User)
async def user(id: str):
    try:
        user = search_user("_id", ObjectId(id))
        return user if user else JSONResponse(content=router.responses[status.HTTP_404_NOT_FOUND],status_code=status.HTTP_404_NOT_FOUND)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID no válido")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)#Status code por defecto cuando todo sale bien
async def user(user: User):
    if type(search_user("email", user.email)) == User:#Si encuentra al usuario lanza la excepcion
        raise HTTPException(status.HTTP_409_CONFLICT, detail=router.responses[status.HTTP_409_CONFLICT])#Devolvemos un status si la operacion fue mal
    try:
        user_dict = dict(user)
        del user_dict['id']
        user_id = db_client.users.insert_one(user_dict).inserted_id
        new_user_data = user_schema(db_client.users.find_one({"_id": user_id}))
        if not new_user_data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear el usuario")
        #Devuelve un json, toca transformarlo en un objeto user
        return User(**new_user_data)##Le paso todos los campos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/", response_model=User)
async def user(user: User):
    try:
        user_dict = dict(user)
        del user_dict['id']
        if not db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict):
            return JSONResponse(content=router.responses[status.HTTP_404_NOT_FOUND],status_code=status.HTTP_404_NOT_FOUND)
        return search_user("_id", ObjectId(user.id))
    except bson_errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID no válido")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")
    
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):
    try:
        found = db_client.users.find_one_and_delete({"_id": ObjectId(id)})
        if not found:
            return JSONResponse(content=router.responses[status.HTTP_404_NOT_FOUND],status_code=status.HTTP_404_NOT_FOUND)
    except bson_errors.InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID no válido")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

#--------------------------------------------
def search_user(field: str, key):
    try:
        return User(**user_schema(db_client.users.find_one({field: key})))
    except:
        return None