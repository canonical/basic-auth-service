"""Helpers for async locking."""

from functools import wraps


def locking(meth):
    """Decorator to execute a class method holding an asyncio.Lock.

    The class the decorated method belongs to must have a "lock" attribute
    which is an asyncio.Lock instance.

    """
    @wraps(meth)
    async def wrapper(oself, *args, **kwargs):
        async with oself.lock:
            return await meth(oself, *args, **kwargs)

    return wrapper
