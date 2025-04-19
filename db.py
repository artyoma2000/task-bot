from asyncpg import create_pool as asyncpg_create_pool

async def create_pool(config):
    return await asyncpg_create_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.dbname,
        host=config.db.host
    )

