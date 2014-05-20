def foo():
    vals = {1:1}
    
    try:
        result = vals[1]
    except KeyError:
        result = 3
    else:
        return result
    finally:
        return result


print foo()
