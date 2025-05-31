import inspect
from functools import wraps

class computed_cached_callable:
    def __init__(self, func):
        self.func = func
        self.cache_property_name = f"_cached_{func.__name__}"
        self.accepts_args = self._accepts_arguments(func)

    def _accepts_arguments(self, func):
        sig = inspect.signature(func)
        params = list(sig.parameters.values())[1:]  # exclude 'self'
        # True if there's at least one param with no default
        return any(p.default is p.empty and p.kind in (p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY) for p in params)

    def __get__(self, owner_class_property, OwnerClass=None):
        # owner_class_property ie func.__name__, is the instance of this descriptor class, defined inside OwnerClass.

        # When owner_class_property is accessed using `OwnerClass.owner_class_property`
        # Return this descriptor class itself to support introspection, access helper methods, etc.
        if owner_class_property is None:
            return self
        
        # When owner_class_property is accessed using `instance.owner_class_property`
        # Return a wrapper function that computes the value if not cached, or returns the cached value if it exists.
        @wraps(self.func)
        def wrapper(*args, **kwargs):
            if self.accepts_args:
                if args or kwargs:
                    # Compute with inputs and cache the result
                    result = self.func(owner_class_property, *args, **kwargs)
                    setattr(owner_class_property, self.cache_property_name, result)
                    return result
                else:
                    if hasattr(owner_class_property, self.cache_property_name):
                        # Return cached result if it exists
                        return getattr(owner_class_property, self.cache_property_name)
                    else:
                        # Raise error otherwise
                        raise AttributeError(f"{self.func.__name__} has not been computed yet. Provide necessary arguments.")
            
            # Return cached result if it exists
            if hasattr(owner_class_property, self.cache_property_name):
                return getattr(owner_class_property, self.cache_property_name)
            
            # Compute and cache otherwise
            result = self.func(owner_class_property)
            setattr(owner_class_property, self.cache_property_name, result)
            return result
        
        return wrapper


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