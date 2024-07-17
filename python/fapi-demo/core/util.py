import asyncio
from datetime import datetime, timezone
import os
import sys
import traceback
from typing import Any, Callable, List, TypeVar



T = TypeVar('T')

async def run_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    # Execute synchronous function in a thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

def format_exception(e: Exception, full_stack: bool = False, skip_external_stacks: bool = True) -> str:
    """
    Format exception with type, message, file, line number and function name.
    
    Args:
        e (Exception): The exception to format.
        full_stack (bool): If True, return the full stack trace. If False, return only the last frame.
    
    Returns:
        str: Formatted exception string.
    """
    exc_type, exc_value, exc_traceback = sys.exc_info()
    working_path = os.getcwd()
    working_path_len = len(working_path)
    if full_stack:
        stack: List[str] = []
        if exc_type is not None:
            stack.append(f"{exc_type.__name__}(\"{str(exc_value)}\")")
        else:
            stack.append(f"Unknown Exception(\"{str(e)}\")")
        
        for frame in traceback.extract_tb(exc_traceback):
            filename, line_number, func_name, _ = frame
            if skip_external_stacks and not filename.startswith(working_path):
                continue
            fname = filename[working_path_len+1:]
            stack.append(f"  at {fname}:{line_number} in {func_name}()")
        return "\n".join(stack)
    else:
        tb = traceback.extract_tb(exc_traceback)
        filename, line_number, func_name, _ = tb[-1] if tb else ("<unknown>", 0, "<unknown>", None)
        return f"{type(e).__name__}(\"{str(e)}\") @ {filename}:{line_number} {func_name}()"

    
if __name__ == "__main__":
    try:
        def inner_function():
            raise ValueError("This is a test error")
        
        def outer_function():
            inner_function()
        
        outer_function()
    except Exception as e:
        print("Single line format:")
        print(format_exception(e))
        print("\nFull stack trace:")
        print(format_exception(e, full_stack=True))
    