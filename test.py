def decorator(func):
    print(func.__code__.co_argcount)
    return func

@decorator
def test(*args):
    print(locals())
    print(*args)

#test(1,2,3)

def accepts(*types):
    def check_accepts(f):
        assert len(types) == f.__code__.co_argcount
        def new_f(*args, **kwds):
            print(args)
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                       "arg %r does not match %s" % (a,t)
            return f(*args, **kwds)
        new_f.__name__ = f.__name__
        return new_f
    return check_accepts

#https://stackoverflow.com/questions/15299878/how-to-use-python-decorators-to-check-function-arguments

def logger():
    def intercepter(func):
        def new_f(*args, **kwargs):
            if func.__code__.co_varnames[0] == "self":
                kwargs.update(zip(func.__code__.co_varnames[1:], args[1:]))
                args = [args[0]]
            else:
                kwargs.update(zip(func.__code__.co_varnames, args))
                args = ()
            print(kwargs)
            return func(*args, **kwargs)
        #new_f.__name__ = func.__name__
        return new_f
    return intercepter

class TestC:
    def __init__(self):
        self.v1 = "tests"
    
    @logger()
    def doathing(self, thing, t2):
        print(self.v1, thing, t2)

@logger()
def func1(a=3,b="hi"):
    print(a**2, b)

@accepts(int,str)
def func2(a=3,b="hi"):
    print(a**2, b)

func1(2,"er")

t = TestC()
t.doathing(123, "321")