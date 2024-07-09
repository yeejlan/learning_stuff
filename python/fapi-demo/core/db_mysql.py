from contextlib import asynccontextmanager
import sys, os
sys.path.append(os.getcwd())
from core import app
from typing import Any, Callable, Union
import aiomysql
import os

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
        pool_recycle=3600,
    )
    return pool

async def release_pool(pool: aiomysql.Pool):
    pool.close()
    await pool.wait_closed()

@asynccontextmanager
async def get_connection(conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool]):
    if isinstance(conn_or_pool, aiomysql.Pool):
        async with conn_or_pool.acquire() as conn:
            yield conn
    else:
        yield conn_or_pool

async def select_one(query, args: tuple, conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool], to: Any=None):
    """
    stmt = "SELECT * FROM employees WHERE ID = %s"
    row = await select_one(stmt, (123,))
    """      
    async with get_connection(conn_or_pool) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            row = await cur.fetchone()
            if row and to:
                return to(**row)
            return row


async def select(query, args: tuple, conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool], to: Any=None):
    """
    stmt = "SELECT * FROM employees WHERE DEPT_ID = %s"
    rows = await select(stmt, (123,))
    """
    async with get_connection(conn_or_pool) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            rows = await cur.fetchall()
            if rows and to:
                return [to(**row) for row in rows]
            return rows


async def insert(query, args: tuple, conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool]) -> int:
    """
    stmt = "INSERT INTO employees (name, phone)
        VALUES ('%s','%s')"
    row_id = await insert(stmt, ('Jane','555-001'))
    """
    async with get_connection(conn_or_pool) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            return cur.lastrowid


async def insert_batch(query:list, records:list, conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool]) -> int:
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
    async with get_connection(conn_or_pool) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.executemany(query, records)
            return cur.rowcount


async def update(query, args: tuple, conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool]) -> int:
    """
    stmt = "UPDATE employees (name, phone)
        VALUES ('%s','%s') WHERE id = %s"
    rowcount = await insert(stmt, ('Jane','555-001', 123))
    """
    async with get_connection(conn_or_pool) as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            return cur.rowcount
        
async def transaction(operations: Callable[[aiomysql.Connection], Any], conn_or_pool: Union[aiomysql.Connection, aiomysql.Pool]):
    async with get_connection(conn_or_pool) as conn:
        await conn.begin()
        try:
            result = await operations(conn)
            await conn.commit()
            return result
        except Exception as e:
            await conn.rollback()
            raise e


if __name__ == "__main__":
    import asyncio

    async def printMysqlVersion():        
        pool = await create_pool()

        res = await select("select version()", (), conn_or_pool=pool)
        print(res)

        async def my_operation(conn: aiomysql.Connection):
            row1 = await select_one("select 1", (), conn_or_pool=conn)
            row2 = await select_one("select 2", (), conn_or_pool=conn)
            return [row1, row2]

        result = await transaction(my_operation, pool)
        print("Transaction successful, result:", result)

        await release_pool(pool)


    asyncio.run(printMysqlVersion())
