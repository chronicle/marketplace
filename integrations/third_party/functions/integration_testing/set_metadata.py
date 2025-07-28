# integration_testing/set_meta.py

def set_metadata(parameters=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"Running test with metadata: {parameters}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
