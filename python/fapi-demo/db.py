from typing import Any
import aiomysql
import os

DictCursor = aiomysql.DictCursor

pool: Any = None

async def create_pool():
    host = os.getenv('DB_HOST', '127.0.0.1')
    port = int(os.getenv('DB_PORT', 3306))
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', '')
    name = os.getenv('DB_NAME', 'dev')
    pool = await aiomysql.create_pool(
        host=host, 
        port=port,
        user=user,
        password=password,
        db=name
    )
    return pool

async def release_pool():
    pool.close()
    await pool.wait_closed()


def get_pool():
    return pool

