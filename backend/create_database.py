import asyncio
from asyncpg import connect

async def create_database():
    """Create the Udbhaw_Db database"""
    # Connect to the default 'postgres' database
    conn = await connect(
        user='postgres',
        password='1234',
        host='localhost',
        database='postgres'
    )
    
    try:
        # Check if database already exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = 'Udbhaw_Db'"
        )
        
        if exists:
            print("Database 'Udbhaw_Db' already exists.")
        else:
            # Create the database
            await conn.execute('CREATE DATABASE "Udbhaw_Db"')
            print("Database 'Udbhaw_Db' created successfully!")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_database())