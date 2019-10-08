class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setattr__

def dispatch(default=None):
    cases = {}
    class Assigner():
        def __init__(self, path):
            self._path = path

        def __getattr__(self, tag):
            if tag != '_path':
                return Assigner((*self._path, tag))

        def __setattr__(self, tag, f):
            if tag != '_path':
                getattr(self, tag)(f)
            else:
                self.__dict__['_path'] = f

        def __call__(self, f):
            nonlocal cases
            cases[self._path] = f

    class Dispatcher():
        def __init__(self):
            if default:
                cases[()] = default

        def __getattr__(self, tag):
            return Assigner((tag,))

        def __setattr__(self, tag, f):
            return getattr(self, tag)(f)

        def __call__(self, *args, **kws):
            tags = tuple(arg.tag for arg in args if tag in arg)
            for i in range(len(tags), -1, -1):
                t = tags[0:i]
                if t in cases:
                    return cases[t](*args, **kws)
            raise ValueError(str(tags))
    return Dispatcher()

evaluate = dispatch()

@evaluate.num
def _(e): return e.val

@evaluate.add
def _(e):
    return evaluate(e.left) + evaluate(e.right)

num = lambda i: dotdict(tag='num', val=i)
add = lambda l, r: dotdict(tag='add', left=l, right=r)

show = dispatch()
show.num = lambda e: str(e.val)
show.add = lambda e: '(' + show(e.left) + '+' + show(e.right) + ')'

exprs = [
    num(1),
    num(2),
    add(num(1), num(2)),
    add(num(1), num(3)),
    add(num(2), num(3)),
    add(num(1), add(num(2), num(3))),
    add(add(num(1), num(2)), num(3)),
]

for e in exprs:
    print('[[', show(e), ']] =', evaluate(e))


equal = dispatch(lambda *_: False)
equal.num.num = lambda a, b: a.val == b.val
equal.add.add = lambda a, b: equal(a.left, b.left) and equal(a.right, b.right)

for e1 in exprs:
    for e2 in exprs:
        print(equal(e1, e2) and 1 or 0, end=' ')
    print()


neg = lambda e: dotdict(tag='neg', negated=e)
evaluate.neg  = lambda e: - evaluate(e.negated)
show.neg      = lambda e: '-' + show(e.negated)
equal.neg.neg = lambda a, b: equal(a.negated, b.negated)

exprs = [
    neg(num(1)),
    add(neg(num(1)), num(2)),
    add(num(1), neg(num(3))),
    neg(add(num(2), num(3))),
    add(num(1), neg(add(num(2), num(3)))),
    add(neg(add(num(1), num(2))), num(3)),
]

for e in exprs:
    print('[[', show(e), ']] =', evaluate(e))

for e1 in exprs:
    for e2 in exprs:
        print(equal(e1, e2) and 1 or 0, end=' ')
    print()

