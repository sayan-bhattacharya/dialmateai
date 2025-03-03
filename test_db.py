import asyncio
import os
from dotenv import load_dotenv
import motor.motor_asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_connection():
    try:
        # Load environment variables
        load_dotenv()

        # Get MongoDB URI and database name
        mongodb_uri = os.getenv('MONGODB_URI')
        db_name = os.getenv('DB_NAME')

        # Print configuration (for debugging)
        print(f"MongoDB URI: {mongodb_uri}")
        print(f"Database Name: {db_name}")

        if not mongodb_uri or not db_name:
            raise ValueError("MongoDB URI or database name not configured")

        # Create client
        client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_uri)
        db = client[db_name]

        # Test connection
        await client.admin.command('ping')
        print("Successfully connected to MongoDB!")

        # Test insert
        result = await db.test.insert_one({"test": "connection"})
        print(f"Test insert successful, id: {result.inserted_id}")

        # Test query
        doc = await db.test.find_one({"test": "connection"})
        print(f"Test query result: {doc}")

        # Cleanup
        await db.test.delete_one({"test": "connection"})
        print("Test cleanup completed")

        # Close connection
        client.close()

    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_connection())
    except Exception as e:
        print(f"Test failed with error: {str(e)}")