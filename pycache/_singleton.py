class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        class_type = type(cls)
        if class_type not in cls._instances:
            cls._instances[class_type] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[class_type]
