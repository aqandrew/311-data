from ..models import db, cache


async def get_last_updated():
    query = db.text("SELECT max(created_time) as last_pulled FROM log WHERE status = 'INFO'")  # noqa
    result = await db.first(query)
    return result.last_pulled.replace(tzinfo=None)


async def get_db_version():
    query = db.text("SELECT version()")
    result = await db.first(query)
    return result.version


async def get_alembic_version():
    query = db.text("SELECT version_num FROM alembic_version")
    result = await db.first(query)
    return result.version_num


async def get_request_types_count():
    query = db.text("SELECT count(*) FROM request_types")
    result = await db.scalar(query)
    return result


async def get_regions_count():
    query = db.text("SELECT count(*) FROM regions")
    result = await db.scalar(query)
    return result


async def get_councils_count():
    query = db.text("SELECT count(*) FROM councils")
    result = await db.scalar(query)
    return result


async def get_service_requests_count():
    query = db.text("SELECT count(*) FROM service_requests")
    result = await db.scalar(query)
    return result


async def get_requests_count():
    query = db.text("SELECT count(*) FROM requests")
    result = await db.scalar(query)
    return result


async def get_cache_info():
    return await cache.raw("info")


async def get_cache_keys():
    return await cache.raw("keys", "*")


async def reset_cache():
    '''need to think about when to call this'''
    await cache.raw("flushdb")
    # config set maxmemory 1000mb
    # config set maxmemory-policy allkeys-lru
    # used memory peak: 286 390 120
    return


async def get_recent_log():
    query = db.text("SELECT * FROM log ORDER BY created_time DESC LIMIT 10")
    result = await db.all(query)
    return result
