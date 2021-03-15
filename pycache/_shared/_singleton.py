class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        class_name = cls.__name__
        if class_name not in cls._instances:
            cls._instances[class_name] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[class_name]
