import motor.motor_asyncio
import asyncio

async def test_connection():
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://mongo:27017')
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
