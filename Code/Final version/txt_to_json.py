import json


def er(x, ms="invalid Syntax"):
    class MyException(Exception):
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message

    raise MyException(ms + "   #line: " + str(x))


def space_del(x):
    v = ''
    for i in x:
        if i != ' ' and i != '\n':
            v += i
    return v


def find_out(s, x):
    k = 0
    for (a, i) in enumerate(s):
        if k == 0 and i == x:
            return a
        k += (i == '(')
        k -= (i == ')')
    return -1


def split_out(s, x):
    res = []
    cur = ''
    k = 0
    s += x
    for i in s:
        if i == x and k == 0:
            res.append(cur)
            cur = ''
        else:
            cur += i
        k += (i == '(')
        k -= (i == ')')
    return res

functions = {}
functions['if'] = {"type": "func", "args": ["cond", "true", "false"]}
functions['drawPoint'] = {"type": "func", "args": ["x", "y", "r", "g", "b"]}
functions['drawLine'] = {"type": "func", "args": ["x0", "y0", "x1", "y1", "r", "g", "b"]}
functions['drawCircle'] = {"type": "func", "args": ["x", "y", "radius", "r", "g", "b"]}
functions['drawEllipse'] = {"type": "func", "args": ["x0", "y0", "x1", "y1", "r", "g", "b"]}

cnt = -1


class Generator:
    def __init__(self, a):
        self.var = a

    def func(self):
        now = self.var
        if now[:5] != 'func ':
            er(cnt)
        now = space_del(now[5:])

        name = ''
        i = 0
        while i < len(now) and now[i] != '(':
            name += now[i]
            i += 1
        if i == len(now):
            er(cnt)
        now = now[i:]
        if now[0] != '(':
            er(cnt)

        parentheses = 0
        k = 0
        for i in range(len(now)):
            if now[i] == '(':
                parentheses += 1
            if now[i] == ')':
                parentheses -= 1
            if parentheses == 0:
                k = i
                break
        if k == len(now) - 1:  # without expression
            er(cnt)
        #print(now[1:k])
        args = now[1:k].split(',')
        for i in range(len(args)):
            args[i] = self.exp_handler([name], args[i])
        now = now[k+1:]
        exp = self.exp_handler([name], now)
        if name == 'main' and args != [] and args != [None]:
            er(cnt, "Main function having input args!")
        elif name == 'main':
            args = []
        if name in functions:
            er(cnt, 'Already existing function')
        functions[name] = {"type": "func", "args": args, "expression": exp}
        return {"type": "function definition", "function name": name, "args": args, "expression": exp}

    def rfunc(self, a, b):
        now = self.var
        if now[:6] != 'rfunc ':
            er(cnt)
        now = space_del(now[6:])

        name = ''
        i = 0
        while i < len(now) and now[i] != '(':
            name += now[i]
            i += 1
        if i == len(now):
            er(cnt)
        now = now[i:]
        if now[0] != '(':
            er(cnt)

        parentheses = 0
        k = 0
        #print(now)
        for i in range(len(now)):
            if now[i] == '(':
                parentheses += 1
            if now[i] == ')':
                parentheses -= 1
            if parentheses == 0:
                k = i
                break
        if k != len(now) - 1:  # expression in the same line
            print("here")
            er(cnt)
        #print(now[1:k])
        args = now[1:k].split(',')
        if len(args) == 0:  # can't be without args
            er(cnt)
        for i in range(len(args)):
            args[i] = self.exp_handler([name], args[i])
        #  recursive expressions
        a = a.split(); b = b.split()
        if a[0] != '0':
            er(cnt+1)
        rec_arg = args.pop()
        rec_val = b[0]
        if name in functions:
            er(cnt, 'Already existing function')

        functions[name] = {}
        functions[name]["type"] = "rfunc"
        base_exp = self.exp_handler([name], space_del(''.join(a[1:])))
        rec_exp = self.exp_handler([name], space_del(''.join(b[1:])))  # self.exp_handler(now)
        new_rec_exp = {}
        new_rec_exp["recursive value name"] = rec_val
        new_rec_exp["expression"] = rec_exp
        functions[name] = {"type": "rfunc", "function name": name, "args": args, "recursive arg": rec_arg,
                           "base expression": base_exp, "recursive expression": new_rec_exp}
        return {"type": "recursive function definition", "function name": name, "args": args, "recursive arg": rec_arg,
                "base expression": base_exp, "recursive expression": new_rec_exp}

    def exp_handler(self, dad, s):
        pos = find_out(s, '+')
        if pos > 0:
            return self.add_plus(s[:pos], s[pos+1:], dad)
        elif pos == 0:
            er(cnt)
        pos = find_out(s, '-')
        if pos > 0:
            return self.add_minus(s[:pos], s[pos + 1:], dad)
        elif pos == 0:
            er(cnt)
        pos = find_out(s, '/')
        if pos > 0:
            return self.add_division(s[:pos], s[pos + 1:], dad)
        elif pos == 0:
            er(cnt)
        pos = find_out(s, '*')
        if pos > 0:
            return self.add_mul(s[:pos], s[pos + 1:], dad)
        elif pos == 0:
            er(cnt)
        pos = find_out(s, '(')
        if pos == -1:
            try:
                s = int(s)
            except:
                if s == '':
                    return
            return s
        name = s[:pos]
        #print(name, dad, functions[name]['type'])
        if name not in functions:
            er(cnt, "Not defined function")

        if name not in dad or functions[name]['type'] == 'rfunc':
            if len(dad) <= 1:
                dad.append(name)
            x = {"type": "function call", "function name": name,
                 "args": [self.exp_handler(dad, x) for x in split_out(s[pos+1:-1], ',')]}
            #print(functions[name]['args'], x['args'], functions[x['function name']]['type'])
            if len(functions[name]['args']) == len(x['args'])and functions[x['function name']]['type'] == 'func':
                return x
            if len(functions[name]['args']) == len(x['args'])-1 and functions[x['function name']]['type'] == 'rfunc':
                return x
            er(cnt, "Number of args are not the same")
        er(cnt)

    def add_plus(self, s1, s2, dad):
        return {'type': '+', 'A': self.exp_handler(dad, s1), 'B': self.exp_handler(dad, s2)}

    def add_minus(self, s1, s2, dad):
        return {'type': '-', 'A': self.exp_handler(dad, s1), 'B': self.exp_handler(dad, s2)}

    def add_division(self, s1, s2, dad):
        return {'type': '/', 'A': self.exp_handler(dad, s1), 'B': self.exp_handler(dad, s2)}

    def add_mul(self, s1, s2, dad):
        return {'type': '*', 'A': self.exp_handler(dad, s1), 'B': self.exp_handler(dad, s2)}


def task(s):
    f = open(s, 'r')
    try:
        s = f.readline()
        H, W = map(int, s.split())
    except:
        er(1, 'Invalid syntax: No Height and Width detected')

    global cnt
    cnt = 2
    functionss = []
    s = f.readline()
    while s != '':
        if s == '\n':
            s = f.readline()
            cnt += 1
            continue
        g = Generator(s)
        if s[0] == 'r':
            #try:
            a = f.readline()
            b = f.readline()
            if a[:4] != ' '*4 or b[:4] != ' '*4:
                er(cnt+1, 'Tab is Missing')
            functionss.append(g.rfunc(a, b))
            cnt += 2
            #except:
            #    er(cnt)
        else:
            functionss.append(g.func())
        cnt += 1
        s = f.readline()
    final = {"height": H, "width": W, "functions": functionss}
    if 'main' not in functions:
        er(cnt, "There is no main function!")
    return json.dumps(final)# ,sort_keys=True, indent=4)

#print((task('sample.sp')))

