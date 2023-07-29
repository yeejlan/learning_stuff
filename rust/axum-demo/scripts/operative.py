import spy;

class MyClass:
    static_var = 0

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b


def add(a, b):
    MyClass.static_var  += 1;
    return MyClass.static_var  + a + b

def log(msg): 
    spy.log(msg)

def handle_http_request(req):
    print(req)