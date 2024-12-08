from PIL import ImageDraw,Image
import json


def er(ms="invalid Syntax"):
    class MyException(Exception):
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message

    raise MyException(ms)


def hex_c(l):
    hx = '0123456789abcdef'
    s = '#'
    for i in l:
        if i > 255 and i < 0:
            print(i, l)
            er('Color out of bound')
        s += (hx[(i//16) % 16] + hx[(i//16) % 16])
    return s


def drawing(shape, args):
    draw = ImageDraw.Draw(img)
    if shape == "Point":
        draw.point([(args[0], args[1])], fill=hex_c(args[2:]))
    if shape == "Line":
        draw.line([(args[0], args[1]), (args[2], args[3])], fill=hex_c(args[4:]))
    if shape == "Circle":
        draw.ellipse((args[0]-args[2], args[1]-args[2], args[0]+args[2], args[1]+args[2]),
                     outline=hex_c(args[3:]))#,

    if shape == "Ellipse":
        draw.ellipse((args[0], args[1], args[2], args[3]), fill=hex_c(args[4:]))
    return 0


def expression_handler(exp, args, vals):
    #bases
    if isinstance(exp, int):
        return exp
    if isinstance(exp, str):
        return vals[args.index(exp)]

    if exp['type'] == '+':
        return expression_handler(exp['A'], args, vals) + expression_handler(exp['B'], args, vals)
    if exp['type'] == '-':
        return expression_handler(exp['A'], args, vals) - expression_handler(exp['B'], args, vals)
    if exp['type'] == '*':
        return expression_handler(exp['A'], args, vals) * expression_handler(exp['B'], args, vals)
    if exp['type'] == '/':
        return expression_handler(exp['A'], args, vals) / expression_handler(exp['B'], args, vals)

    if exp['function name'] == "if":
        if expression_handler(exp["args"][0], args, vals):
            expression_handler(exp["args"][1], args, vals)
        else:
            expression_handler(exp["args"][2], args, vals)
        return 0

    args = [expression_handler(arg, args, vals) for arg in exp["args"]]

    if exp['function name'] in ["drawPoint", "drawLine", "drawCircle", "drawEllipse"]:
        return drawing(exp['function name'][4:], args)

    for now in funcs:
        if now['function name'] == exp['function name']:
            if now['type'] in ['function definition', 'recursive function definition']:
                func = now
    try:
        a = func['type']
    except:
        er("Wrong input file")

    #print(exp, args, vals)

#  simple func
    if func['type'] == 'function definition':
        return expression_handler(func['expression'], func['args'], args)
#  recursive

    r = expression_handler(func['base expression'], func['args'], args)
    new_func_arg = []
    for i in func['args']:
        new_func_arg.append(i)
    new_func_arg.append(func['recursive arg'])
    new_func_arg.append(func['recursive expression']['recursive value name'])
    temp_args = []
    for i in args[:-1]:
        temp_args.append(i)
    temp_args.append(0)
    temp_args.append(0)
    for i in range(1, args[-1]+1):
        temp_args[-2:] = [i, r]
        #  print(temp_args, '\n', temp_args)
        r = expression_handler(func['recursive expression']['expression'], new_func_arg, temp_args)
    return r


def main(json_load, name):
    #print(11111111111)
    global funcs
    funcs = json_load['functions']
    global img
    img = Image.new("RGB", (json_load['width'], json_load['height']), (255, 255, 255))

    for now in funcs:
        if now['function name'] == 'main':
            if now['type'] in ['function definition', 'recursive function definition']:
                func = now

    expression_handler(func['expression'], [], [])
    img.save(name+".jpg", "JPEG")
    img.show()
    #print(2222222222222)
'''
f = open("mj.json")
S = "".join(f.readlines())
f.close()
J1 = json.loads(S)
print(J1)
main(J1, '1')
'''