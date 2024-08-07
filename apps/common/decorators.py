from django.db.transaction import Atomic
from asgiref.sync import sync_to_async


class AsyncAtomicContextManager(Atomic):
    def __init__(self, using=None, savepoint=True, durable=False):
        super().__init__(using, savepoint, durable)

    async def __aenter__(self):
        await sync_to_async(super().__enter__)()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await sync_to_async(super().__exit__)(exc_type, exc_value, traceback)


def aatomic(fun):
    async def wrapper(*args, **kwargs):
        async with AsyncAtomicContextManager():
            return await fun(*args, **kwargs)

    return wrapper


# async def test():
#     async with AsyncAtomicContextManager():
