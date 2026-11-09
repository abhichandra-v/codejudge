def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    product = 1
    for k in range(2, n + 1):
        product *= k
    return product
