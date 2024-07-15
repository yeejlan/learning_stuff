import functools
import sys
import os
import traceback
from typing import Any, Callable, Coroutine, cast

from pydantic import BaseModel

class GoResult(BaseModel):
    error: str = ''
    data: Any = None


def format_exception(e: Exception) -> str:
    """Format exception with type, message, file, line number and function name."""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)
    filename, line_number, func_name, _ = tb[-1]
    working_path = os.getcwd()
    filename = filename.lstrip(working_path)
    return f"{type(e).__name__}(\"{str(e)}\") @ {filename}:{line_number} {func_name}()"

def catch_error_as_goresult() -> Callable:
    """
    A decorator that wraps an asynchronous function to return an AsyncResult object.

    This decorator catches any exceptions raised by the wrapped function and returns
    them as part of the AsyncResult as a formatted error string. If no exception occurs, 
    the function's return value is wrapped in the AsyncResult.

    Returns:
        Callable: A decorator function that can be applied to an asynchronous function.

    Usage:
        @catch_error_as_goresult()
        async def my_async_function():
            # function implementation

    The decorated function will return an AsyncResult object, which can be used as follows:
        result = cast(GoResult, await await my_async_function())
        if result.error:
            # handle error string
        else:
            # use result.data
    """
    def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine[Any, Any, GoResult]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> GoResult:
            try:
                result = await func(*args, **kwargs)
                return GoResult(data=result)
            except Exception as e:
                error_message = format_exception(e)
                return GoResult(error=error_message)
        return wrapper
    return decorator


if __name__ == "__main__":
    import asyncio

    @catch_error_as_goresult()
    async def example_function(x: int, y: int) -> int:
        await asyncio.sleep(0.01)
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x // y

    async def main():
        result = cast(GoResult, await example_function(10, 2))
        if result.error:
            print(f"Error occurred: {result.error}")
        else:
            print(f"Result: {result.data}")

        result = cast(GoResult, await example_function(10, 0))
        if result.error:
            print(f"Error occurred: {result.error}")
        else:
            print(f"Result: {result.data}")
            

    asyncio.run(main())