"""Database transaction helpers."""

from .model import Model

from functools import wraps


def transact(meth):
    """Decorator to execute a class method in method in a transaction.

    The class decorated method belongs to must have an "engine" attribute with
    the database engine.

    The wrapped function must accept a Model instance as first argument.

    """
    @wraps(meth)
    async def wrapper(oself, *args, **kwargs):
        engine = oself.engine

        async with engine.acquire() as conn:
            async with conn.begin():
                await conn.execute(
                    'SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
                return await meth(oself, Model(conn), *args, **kwargs)

    return wrapper


async def run_in_transaction(engine, model_method, *args, **kwargs):
    """Run the named Model method in a transaction."""
    async with engine.acquire() as conn:
        async with conn.begin():
            await conn.execute(
                'SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')
            meth = getattr(Model(conn), model_method)
            return await meth(*args, **kwargs)
