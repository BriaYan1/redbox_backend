# redbox_backend/RedBoxAppBackend/mongo_client.py
#
# Cliente de MongoDB independiente del ORM de Django/Postgres.
# Se usa SOLO para las colecciones que no necesitan relaciones ni ACID
# cruzado, como el registro de eventos de acceso biométrico.
#
# Instalación:
#   pip install pymongo --break-system-packages   (si estás en el contenedor)
#   pip install pymongo                            (en tu entorno normal de Windows)
#
# Variables de entorno (agrégalas a tu .env, junto a las de Postgres):
#   MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?retryWrites=true&w=majority
#   MONGO_DB_NAME=redbox_biometria
#
# Recomendación: usa MongoDB Atlas (capa gratuita M0). Así no necesitas
# instalar Mongo en tu máquina de Windows ni en el servidor de pruebas,
# y puedes mostrar el clúster real en la sustentación.

import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

_client = None
_db = None


def get_mongo_db():
    """
    Devuelve el objeto de base de datos de Mongo, creando la conexión
    una sola vez (patrón singleton) para no abrir un socket nuevo
    en cada request.
    """
    global _client, _db
    if _db is None:
        uri = os.environ.get("MONGO_URI")
        db_name = os.environ.get("MONGO_DB_NAME", "redbox_biometria")

        if not uri:
            raise RuntimeError(
                "Falta la variable de entorno MONGO_URI en tu archivo .env"
            )

        _client = MongoClient(uri, server_api=ServerApi("1"))
        _db = _client[db_name]
    return _db


def get_access_logs_collection():
    """Colección donde se registra cada intento de acceso biométrico."""
    return get_mongo_db()["access_logs"]
