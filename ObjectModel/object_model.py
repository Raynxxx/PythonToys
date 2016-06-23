
MISSING = object()


class Base(object):
    """  the ultimate base class of the inheritance hierarchy """

    def __init__(self, cls, fields):
        self.cls = cls
        self._fields = fields

    def read_attr(self, field_name):
        return self._read_dict(field_name)

    def write_attr(self, field_name, value):
        self._write_dict(field_name, value)

    def isinstance(self, cls):
        return self.cls.is_subclass(cls)

    def call_method(self, method_name, *args):
        method = self.cls.read_from_class(method_name)
        return method(self, *args)

    def _read_dict(self, field_name):
        return self._fields.get(field_name, MISSING)

    def _write_dict(self, field_name, value):
        self._fields[field_name] = value


class Instance(Base):

    def __init__(self, cls):
        assert isinstance(cls, Class)
        Base.__init__(self, cls, {})


class Class(Base):

    def __init__(self, name, base_class, fields, metaclass):
        Base.__init__(self, metaclass, fields)
        self.name = name
        self.base_class = base_class

    def method_resolution_order(self):
        if self.base_class is None:
            return [self]
        else:
            return [self] + self.base_class.method_resolution_order()

    def is_subclass(self, cls):
        return cls in self.method_resolution_order()

    def read_from_class(self, method_name):
        for cls in self.method_resolution_order():
            if method_name in cls._fields:
                return cls._fields[method_name]
        return MISSING

Object = Class(name='object', base_class=None, fields={}, metaclass=None)

Type = Class(name='type', base_class=Object, fields={}, metaclass=None)

Type.cls = Type
Object.cls = Type
