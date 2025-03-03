# src/core/database.py
import motor.motor_asyncio
from pymongo.errors import ConnectionFailure
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB database"""
        if cls._client is not None:
            return cls._db

        try:
            load_dotenv()
            mongodb_uri = os.getenv('MONGODB_URI')
            db_name = os.getenv('DB_NAME')

            if not mongodb_uri or not db_name:
                raise ValueError("MongoDB URI or database name not configured")

            # Create motor client
            cls._client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_uri)
            cls._db = cls._client[db_name]

            # Test connection
            await cls._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {db_name}")

            # Create indexes
            await cls._create_indexes()

            return cls._db

        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    @classmethod
    async def _create_indexes(cls):
        """Create necessary indexes"""
        try:
            # Create indexes for conversations collection
            await cls._db.conversations.create_index([("user_id", 1)])
            await cls._db.conversations.create_index([("timestamp", -1)])

            # Create indexes for users collection
            await cls._db.users.create_index([("telegram_id", 1)], unique=True)
            await cls._db.users.create_index([("username", 1)])

            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
            raise

    @classmethod
    async def close(cls):
        """Close database connection"""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("Database connection closed")