from typing import Any, List
from collections.abc import Hashable

import redis.asyncio as aioredios
from pydantic import TypeAdapter, BaseModel
from functools import wraps

from app.config import settings

redis_client = aioredios.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=settings.REDIS_CAHCE_DB, 
    decode_responses=True # При = True будет возвращать строки, а не байты
)

def build_redis_key(main_part: str, another_part: List[Any]) -> str:
    another_part_str_valid = ":".join([str(part) for part in another_part if isinstance(part, (str, int))])

    if main_part:
        return main_part + ":" + another_part_str_valid
    return another_part_str_valid

def unite_args_kwargs(*args: tuple[Any], **kwargs: dict[Hashable, Any]):
    united_args = list(args)
    united_args.extend(list(kwargs.values()))

    return united_args

def cache_or_db(redis_key: str, serialization_type: BaseModel, build_key: bool = True):
    def inner_1(func):
        type_adapter = TypeAdapter(serialization_type)

        @wraps(func)
        async def inner_2(*args: tuple[Any], **kwargs: dict[Hashable, Any]):
            actual_redis_key = redis_key

            if build_key:
                all_args = unite_args_kwargs(*args, **kwargs)
                actual_redis_key = build_redis_key(redis_key, all_args)

            cache = await redis_client.get(actual_redis_key)
            if cache is not None:
                print("Берём из кэша")
                return type_adapter.validate_json(cache)

            res = await func(*args, **kwargs)
            res_validated = None

            if res is not None:
                res_validated = type_adapter.validate_python(res)
                res_json = type_adapter.dump_json(res_validated)
                await redis_client.set(name=actual_redis_key, value=res_json, ex=settings.CACHE_TTL)

            print("Берём из БД")
            return res_validated
        
        return inner_2
    return inner_1

def invalidate_cache(redis_main_key_piece: str):
    def inner_1(func):
        @wraps(func)
        async def inner_2(*args, **kwargs):
            result = await func(*args, **kwargs)

            cursor = 0
            while True:
                cursor, keys = await redis_client.scan(cursor=cursor, match=f"{redis_main_key_piece}*", count=100)

                if keys:
                    await redis_client.delete(*keys)

                if cursor == 0:
                    break
                
            return result
    
        return inner_2
    return inner_1