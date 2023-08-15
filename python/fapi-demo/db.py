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


async def select_one(query, *args, pool = pool):
    """
    stmt = "SELECT * FROM employees WHERE ID = %s"
    row = await select_one(stmt, (123,))
    """      
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            return await cur.fetchone()


async def select(query, *args, pool = pool):
    """
    stmt = "SELECT * FROM employees WHERE DEPT_ID = %s"
    rows = await select(stmt, (123,))
    """       
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            return await cur.fetchall()


async def insert(query, *args, pool = pool):
    """
    stmt = "INSERT INTO employees (name, phone)
        VALUES ('%s','%s')"
    row_id = await insert(stmt, ('Jane','555-001'))
    """    
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            return cur.lastrowid


async def insert_batch(query, *args, pool = pool):
    """
    data = [
        ('Jane','555-001'),
        ('Joe', '555-001'),
        ('John', '555-003')
    ]
    stmt = "INSERT INTO employees (name, phone)
        VALUES ('%s','%s')"
    rowcount = await insert_batch(stmt, data)
    """
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.executemany(query, args)
            return cur.rowcount


async def update(query, *args, pool = pool):
    """
    stmt = "UPDATE employees (name, phone)
        VALUES ('%s','%s') WHERE id = %s"
    rowcount = await insert(stmt, ('Jane','555-001', 123))
    """        
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            return cur.rowcount