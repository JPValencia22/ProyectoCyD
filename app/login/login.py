import os
import nest_asyncio
from config.db_login_config import MONGODB_CONFIG_LOGIN
from motor.motor_asyncio import AsyncIOMotorClient

nest_asyncio.apply()

client = AsyncIOMotorClient(host=MONGODB_CONFIG_LOGIN['host'], port=MONGODB_CONFIG_LOGIN['port'])
db = client[MONGODB_CONFIG_LOGIN['database']]
collection = db[MONGODB_CONFIG_LOGIN['collection']]

async def search_user():
    email = os.getenv("RECIPIENT_EMAIL")
    password = os.getenv("RECIPIENT_PASSWORD")
    
    print(f"Buscando usuario con email: {email} y contraseña: {password}")
    
    user = await collection.find_one({"email": email, "security_key": password})
    if user:
        print("Usuario encontrado")
        return "Usuario encontrado"
    else:
        print("Usuario no encontrado")
        return "Usuario no encontrado"