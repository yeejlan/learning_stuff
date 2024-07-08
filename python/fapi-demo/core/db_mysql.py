import sys, os
sys.path.append(os.getcwd())
from core import app
from typing import Any, Callable
import aiomysql
import os


DictCursor = aiomysql.DictCursor

config = app.config

async def create_pool(prefix :str = 'DB') -> aiomysql.Pool:
    host = config.get(f'{prefix}_HOST', '127.0.0.1')
    port = config.getInt(f'{prefix}_PORT', 3306)
    user = config.get(f'{prefix}_USER', 'root')
    password = config.get(f'{prefix}_PASSWORD', '')
    name = config.get(f'{prefix}_NAME', 'dev')
    echo = config.getBool(f'{prefix}_ECHO', False)
    connect_timeout = config.getInt(f'{prefix}_CONNECT_TIMEOUT', 5)
    minsize = config.getInt(f'{prefix}_MINSIZE', 1)
    maxsize = config.getInt(f'{prefix}_MAXSIZE', 10)
    pool = await aiomysql.create_pool(
        host=host, 
        port=port,
        user=user,
        password=password,
        db=name,
        echo=echo,
        connect_timeout=connect_timeout,
        minsize=minsize,
        maxsize=maxsize,
        autocommit=True,
    )
    return pool

async def release_pool(pool: aiomysql.Pool):
    pool.close()
    await pool.wait_closed()


async def select_one(query, *args, pool: aiomysql.Pool, to: Any):
    """
    stmt = "SELECT * FROM employees WHERE ID = %s"
    row = await select_one(stmt, (123,))
    """      
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            row = await cur.fetchone()
            if row and to:
                return to(**row)
            return row


async def select(query, *args, pool: aiomysql.Pool, to: Any):
    """
    stmt = "SELECT * FROM employees WHERE DEPT_ID = %s"
    rows = await select(stmt, (123,))
    """
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            rows = await cur.fetchall()
            if rows and to:
                return [to(**row) for row in rows]
            return rows


async def insert(query, *args, pool: aiomysql.Pool) -> int:
    """
    stmt = "INSERT INTO employees (name, phone)
        VALUES ('%s','%s')"
    row_id = await insert(stmt, ('Jane','555-001'))
    """
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            return cur.lastrowid


async def insert_batch(query:list, records:list, pool: aiomysql.Pool) -> int:
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
            await cur.executemany(query, records)
            return cur.rowcount


async def update(query, *args, pool: aiomysql.Pool) -> int:
    """
    stmt = "UPDATE employees (name, phone)
        VALUES ('%s','%s') WHERE id = %s"
    rowcount = await insert(stmt, ('Jane','555-001', 123))
    """
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cur:
            await cur.execute(query, args)
            return cur.rowcount
        
async def transaction(operation: Callable[[aiomysql.DictCursor], Any], pool: aiomysql.Pool):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await conn.begin()
            try:
                result = await operation(cur)
                await conn.commit()
                return result
            except Exception as e:
                await conn.rollback()
                raise e


if __name__ == "__main__":
    import asyncio
    from core import db_mysql


    async def printMysqlVersion():        
        pool = await db_mysql.create_pool()

        res = await db_mysql.select("select version()", to=dict, pool=pool)
        print(res)

        async def my_operation(cur: aiomysql.DictCursor):
            await cur.execute("select 1", ())
            await cur.execute("select 2", ())
            return await cur.fetchall()

        result = await db_mysql.transaction(my_operation, pool)
        print("Transaction successful, result:", result)

        await db_mysql.release_pool(pool)


    asyncio.run(printMysqlVersion())
