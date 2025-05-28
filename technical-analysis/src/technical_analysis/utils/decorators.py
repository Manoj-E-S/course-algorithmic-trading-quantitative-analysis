import inspect
from functools import wraps

def mutually_exclusive_args(*exclusive_args):
    """
    Decorator factory to ensure that only one of the specified arguments is provided.
    Raises ValueError if more than one argument is provided.
    """
    def decorator(func):
        func_sig: inspect.Signature = inspect.signature(func)
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bind args and kwargs to parameter names
            bound_args: inspect.BoundArguments = func_sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Check which mutually exclusive args are not None
            provided = [
                arg for arg in exclusive_args
                if bound_args.arguments.get(arg) is not None
            ]

            if len(provided) != 1:
                err: str = f"Exactly one of {exclusive_args} must be provided. You provided: {provided}"
                raise ValueError(err)

            return func(*args, **kwargs)
        return wrapper
    
    return decorator


def optionally_overridable(func):
    """Marker: The method decorated with optionally_overridable may optionally be overridden in subclasses."""
    return func


def override(func):
    """Marker: Used in subclasses to indicate that the method overrides a method in the parent class for better readability."""
    return func