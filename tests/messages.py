from collections.abc import AsyncIterator, Iterator

message = "Hi!"


def sync_callable_msg() -> str:
    return message


async def async_callable_msg() -> str:
    return message


async def async_generator_msg() -> AsyncIterator[str]:
    yield message


def sync_generator_msg() -> Iterator[str]:
    yield message


class _C:
    def __call__(self) -> str:
        return message


class _AC:
    async def __call__(self) -> str:
        return message


sync_callable_class_message = _C()
async_callable_class_message = _AC()
