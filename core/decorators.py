import concurrent.futures
import functools


def timeout(seconds):
    """
    A decorator to timeout a function after a specified number of seconds.
    Uses concurrent.futures for thread-safe and cross-platform compatibility.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"Function '{func.__name__}' timed out after {seconds} seconds")
        return wrapper
    return decorator
