class SingletonMeta(type):
    """
    A metaclass to implement singleton design pattern on any class that uses it
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]