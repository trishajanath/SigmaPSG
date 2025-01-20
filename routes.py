from asyncio.log import logger
from fastapi import HTTPException
from models import User, UserCreate, UserRead, UserInDB
from typing import Optional
import motor.motor_asyncio
from bson import ObjectId
from passlib.context import CryptContext
from auth import get_password_hash, verify_password, create_access_token
from datetime import timedelta

# Use 'mongo' as the hostname if using Docker Compose
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://mongo:27017')

database = client.UserList
collection = database.user

async def fetch_user_by_id(user_id: str):
    try:
        document = await collection.find_one({"_id": ObjectId(user_id)})
        if document:
            document["id"] = str(document.pop("_id"))
            return UserRead(**document)
        return None
    except Exception as e:
        print(f"Error fetching user by ID: {e}")
        return None

async def fetch_all_users():
    users = []
    cursor = collection.find({})
    async for document in cursor:
        document["id"] = str(document.pop("_id"))
        users.append(UserRead(**document))
    return users

async def create_user(user: UserCreate):
    try:
        user_obj = UserInDB.create_user(user)
        document = user_obj.dict(exclude={"hashed_password"})
        result = await collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        return UserRead(**document)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def update_user(user_id: str, user: UserCreate):
    user_obj = UserInDB.create_user(user)  # Create user object with hashed password
    document = user_obj.dict(exclude={"password"})
    await collection.update_one({"_id": ObjectId(user_id)}, {"$set": document})
    updated_document = await collection.find_one({"_id": ObjectId(user_id)})
    if updated_document:
        updated_document["id"] = str(updated_document.pop("_id"))
        return UserRead(**updated_document)
    return None

async def remove_user(user_id: str):
    result = await collection.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0
