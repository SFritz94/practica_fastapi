from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/products",#Forma de darle un prefijo o contexto a la ruta
    tags=["products"],#Forma de agrupar las rutas en la documentacion
    responses={404: {"message": "Producto no encontrado"}}#Respuesta por defecto en caso de no encontrar el producto
)

products_list = ["Prod1","Prod2","Prod3","Prod4","Prod5"]

@router.get("/")
async def products():
    return products_list

@router.get("/{id}")
async def products(id: int):
    try:
        return products_list[id]
    except IndexError:
        return JSONResponse(content=router.responses[404], status_code=404)