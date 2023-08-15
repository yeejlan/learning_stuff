import db


async def get_user_by_id(user_id: int):
    query = 'select * from users where id = %s'
    async with db.pool.acquire() as conn:
        async with conn.cursor(db.DictCursor) as cur:
            await cur.execute(query, user_id)
            return await cur.fetchone()
        