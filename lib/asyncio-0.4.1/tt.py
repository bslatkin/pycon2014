def foo():
    yield 42
    yield 'abc'

def bar():
    yield from foo()

def baz():
    yield from bar()

b = baz()
x = next(b)
print(x)
print(b.gi_frame.f_code.co_name)
print(b.gi_frame.f_back)
