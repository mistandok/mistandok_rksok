from typing import Hashable


class ObjectSerializer:
    """This class setup class factory for any classes."""
    def __init__(self):
        self._objects = {}

    def register_format(self, key: Hashable, object: object):
        """Register object in serializer"""
        self._objects[key] = object

    def get_serializer(self, key: Hashable):
        """Get definite serializer."""
        object = self._objects.get(key)
        if not object:
            raise ValueError(key)
        return object


if __name__ == '__main__':
    pass