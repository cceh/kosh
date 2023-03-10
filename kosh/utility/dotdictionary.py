class dotdictionary(dict):
    """
    ``dotdictionary`` wrapper class around the built-in ``dict`` to allow
    dot-operator access to its values.

    See:
    - https://stackoverflow.com/a/23689767
    - https://stackoverflow.com/a/13520518

    :param dict: The built-in ``dict`` to wrap.
    :returns: The wrapped ``dict`` as ``dotdictionary``
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
        for key, value in dict(*args, **kwargs).items():
            if hasattr(value, "keys"):
                value = dotdictionary(value)
            self[key] = value
