#Encargado de gestionar la conexion a la base de datos (mongodb)
from pymongo import MongoClient

#Conexion a base de datos local
#db_client = MongoClient().local

#Conexion a base de datos remota
db_client = MongoClient(
    "mongodb+srv://santiagofritz94:uB0vLiFGvfaPUKRI@cluster0.sgwc1by.mongodb.net/?retryWrites=true&w=majority"
    ).test