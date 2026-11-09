import math


def is_perfect_square(n):
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n
