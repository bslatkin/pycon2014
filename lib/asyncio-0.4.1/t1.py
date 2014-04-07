import traceback

def inner():
    1/0

def middle():
    inner()

def outer():
    middle()

def main():
    try:
        outer()
    except Exception:
        print('[[[')
        traceback.print_exc(limit=20)
        print(']]]')

main()
