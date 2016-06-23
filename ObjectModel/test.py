from ObjectModel.object_model import Class, Object, Instance, Type
from unittest import TestCase


class TestObjectModel(TestCase):

    def test_read_write_field(self):
        # Python code
        class A(object):
            pass

        obj = A()
        obj.a = 1
        assert obj.a == 1

        obj.b = 5
        assert obj.b == 5

        obj.a = 2
        assert obj.a == 2
        assert obj.b == 5

        # self Object model code
        B = Class(name='B', base_class=Object, fields={"a": 3}, metaclass=Type)

        obj2 = Instance(B)
        obj2.write_attr('a', 1)
        assert obj2.read_attr('a') == 1

        obj2.write_attr('b', 5)
        assert obj2.read_attr('b') == 5

        obj2.write_attr('a', 2)
        assert obj2.read_attr('a') == 2
        assert obj2.read_attr('b') == 5

    def test_read_write_class_field(self):
        # Python code
        class A(object):
            pass

        A.a = 1
        assert A.a == 1
        A.a = 6
        assert A.a == 6

        # self Object model code
        B = Class(name='B', base_class=Object, fields={"a": 3}, metaclass=Type)
        assert B.read_attr('a') == 3

        B.write_attr('a', 6)
        assert B.read_attr('a') == 6

    def test_isinstance(self):
        # Python code
        class A(object):
            pass

        class B(A):
            pass

        b = B()
        assert isinstance(b, B)
        assert isinstance(b, A)
        assert isinstance(b, object)
        assert not isinstance(b, type)

        # self Object model code
        C = Class(name='C', base_class=Object, fields={}, metaclass=Type)
        D = Class(name='D', base_class=C, fields={}, metaclass=Type)
        d = Instance(D)
        assert d.isinstance(D)
        assert d.isinstance(C)
        assert d.isinstance(Object)
        assert not d.isinstance(Type)

    def test_call_method_simple(self):
        # Python code
        class A(object):

            def __init__(self):
                self.x = 1

            def f(self):
                return self.x + 1

        obj = A()
        assert obj.f() == 2

        class B(A):
            pass

        obj = B()
        obj.x = 1
        assert obj.f() == 2  # works on subclass too

        def func_A(self):
            return self.read_attr('x') + 1

        A = Class(name='A', base_class=Object, fields={'f': func_A}, metaclass=Type)
        obj = Instance(A)
        obj.write_attr('x', 1)
        assert obj.call_method('f') == 2

        B = Class(name='B', base_class=A, fields={}, metaclass=Type)
        obj = Instance(B)
        obj.write_attr('x', 2)
        assert obj.call_method('f') == 3

    def test_call_method_subclassing_arguments(self):
        # Python code
        class A(object):

            def __init__(self):
                self.x = 1

            def g(self, arg):
                return self.x + arg

        obj = A()
        obj.x = 1
        assert obj.g(4) == 5

        class B(A):
            def g(self, arg):
                return self.x + arg * 2

        obj = B()
        obj.x = 4
        assert obj.g(4) == 12

        def g_A(self, arg):
            return self.read_attr('x') + arg

        A = Class(name="A", base_class=Object, fields={'g': g_A}, metaclass=Type)
        obj = Instance(A)
        obj.write_attr('x', 1)
        assert obj.call_method('g', 4) == 5

        def g_B(self, arg):
            return self.read_attr('x') + arg * 2

        B = Class(name="B", base_class=A, fields={'g': g_B}, metaclass=Type)
        obj = Instance(B)
        obj.write_attr('x', 4)
        assert obj.call_method('g', 4) == 12


