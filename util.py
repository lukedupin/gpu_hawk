import re


def xlist( ary ):
    return list(ary) if ary is not None else []


def xtuple( tup ):
    return tuple(tup) if tup is not None else tuple()


def xstr( s, none='' ):
    return str(s) if s is not None else none


def xint( s, none=0, undefined=None ):
    try:
      if s == "undefined":
        return undefined
      return int(s) if s is not None and s != 'NaN' else none
    except ValueError:
        #Floating points and trailing letters wont fool me!!!
        m = re.search('^[-+]?[0-9]+', s)
        if m:
            return int(m.group(0))

        #can't go any further
        return none
    except TypeError:
        return none


def xfloat( s, none=0.0, undefined=None ):
    try:
        if s == "undefined":
            return undefined
        f = float(s) if s is not None and s != 'NaN' else none
        if math.isnan(f):
            return none
        return f
    except ValueError:
        #trailing letters wont fool me!!!
        m = re.search('^[-+]?[0-9]*\.?[0-9]+', s )
        if m:
            return float(m.group(0))

        #Can't go any further
        return none
    except TypeError:
        return none


def xbool( s, none=False, undefined=False ):
    #Are we string? try to figure out what that means
    if isinstance( s, str ):
        s = s.lower()
        if s == 'true':
            return True
        elif s == 'none' or s == 'null':
            return none
        elif s == 'undefined':
            return undefined
        else:
            return False

    #Special case none
    elif s is None:
        return none
    else:
        return bool(s)

def xlen( x, none=0 ):
    return len(x) if x is not None else none

# Cap a value between the given bounds
def cap( val, high, low=None ):
    if not low:
        low = -high
    if val > high:
        val = high
    elif val < low:
        val = low

    return val
