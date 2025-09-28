# def repeat(num):
#     def my_decorator(func):
#         def wrapper():
#             for i in range(num):
#                 func()
#         return wrapper
#     return my_decorator





print("salam")


from functools import wraps

def repeat(num):
    def my_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for i in range(num):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return my_decorator
@repeat(num=3)
def say_hello():
    print("سلام. به مجله مکتب خونه خوش آمدید")


say_hello()