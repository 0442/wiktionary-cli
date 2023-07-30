from tools import options

def log(*msg):
    if options.VERBOSE:
        print(*msg)
