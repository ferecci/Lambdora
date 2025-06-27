from values import Builtin, valueToString
from printer import lambPrint

def lambMakeTopEnv():
    env = {}

    # Curried addition
    def add(x):
        return Builtin(lambda y: x + y) if isinstance(x, int) else TypeError()

    def pr(x):
        print(valueToString(x))
        return x

    env['+'] = Builtin(add)
    env['print'] = Builtin(pr)
    env['true'] = True
    env['false'] = False

    return env