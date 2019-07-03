
class MatchableString(str):
    pass

def match_pattern(xs, ps):
    if callable(ps):
        return ps(xs)
    if isinstance(ps, dict):
        if not isinstance(xs, dict):
            return None
        ks = set(xs.keys())
        if ks != set(ps.keys()):
            return None
        return match_pattern([xs.get(k) for k in ks], [ps.get(k) for k in ks])
    tuplelike = lambda us: isinstance(us, list) or isinstance(us, tuple)
    if tuplelike(ps):
        if not tuplelike(ps) or len(xs) != len(ps):
            return None
        ms = [ match_pattern(x, p) for x, p in zip(xs, ps) ]
        if all(m is not None for m in ms):
            return sum(ms, [])
        else:
            return None
    if isinstance(ps, MatchableString):
        return [] if xs == ps else None
    raise ValueError(f'{ps} is not a valid pattern')

class Match():
    """
    >>> m = Match(['plop', ['flop', 1], {"glop":2}])
    >>> def var(name):
    ...     return lambda x: [(name, x)]
    >>> a, b, c, d = map(var, 'abcd')
    >>> m==[a,b], m.matches()
    (False, None)
    >>> (m.plop,)   # change this raised exception?
    (None,)
    >>> m==[a,b,c], m.matches()
    (True, {'a': 'plop', 'b': ['flop', 1], 'c': {'glop': 2}})
    >>> m.a
    'plop'
    >>> m==[a,b,c,d], m.matches()
    (False, None)
    >>> m==[a,[b,d],c], m.b, m.d
    (True, 'flop', 1)
    >>> m==[a,b,{"glop":c}], m.c
    (True, 2)
    >>> m==[a,b,{}], m==[a,b,{"flop":c}], m==[a,b,{"flop":c, "glop":d}]
    (False, False, False)
    >>> m==['plop',a,b]
    Traceback (most recent call last):
        ...
    ValueError: plop is not a valid pattern
    >>> m==[MatchableString('plop'),a,b]
    True
    """
    def __init__(self, x):
        self.__x = x
        self.__m = None

    def __eq__(self, p):
        m = match_pattern(self.__x, p)
        if m is None:
            self.__m = None
            return False
        else:
            self.__m = dict(m)
            return True

    def __getattr__(self, s):
        if self.__m:
            return self.__m.get(s, None)
        else:
            return None

    def matches(self):
        return self.__m

from contextlib import contextmanager
@contextmanager
def match(x):
    yield Match(x)

def con(name, N=None):
    def mk(*xs):
        assert N is None or len(xs) == N
        return (MatchableString(name), *xs)
    return mk

App = con('App', 2)
Lam = con('Lam', 2)
Var = con('Var', 1)

_ = lambda x: []
def var(name):
    return lambda x: [(name, x)]

x, y, e1, e2 = map(var, 'x y e1 e2'.split())

_c = 0
def refresh(e, d=None):
    global _c
    if d is None:
        return refresh(e, {})
    with match(e) as m:
        if m == Var(x):
            return Var(d[m.x]) if m.x in d else e
        elif m == App(e1, e2):
            return App(refresh(m.e1, d), refresh(m.e2, d))
        elif m == Lam(x, e1):
            d[m.x] = f'_{_c}'
            _c += 1
            return Lam(d[m.x], refresh(m.e1, d))
        else:
            raise ValueError()

def subst(e, x, to):
    # requires x not in BV(e)
    with match(e) as m:
        if m == Var(MatchableString(x)):
            return refresh(to)
        elif m == Var(y):
            return e
        elif m == App(e1, e2):
            return App(subst(m.e1, x, to), subst(m.e2, x, to))
        elif m == Lam(y, e1):
            return Lam(y, subst(m.e1, x, to), subst(m.e2, x, to))
        else:
            raise ValueError()

def beta(e):
    with match(e) as m:
        if m == App(Lam(x, e1), e2):
            return beta(subst(m.e1, m.x, m.e2))
        elif m == App(e1, e2):
            return App(beta(m.e1), beta(m.e2))
        elif m == Lam(x, e1):
            return Lam(m.x, beta(m.e1))
        else:
            return e

print(beta(App(Lam('x', App(Var('y'), Var('x'))), Lam('z', Var('z')))))
