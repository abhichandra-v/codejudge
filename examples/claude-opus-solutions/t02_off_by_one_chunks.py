def num_chunks(length, n):
    # ceiling division without floating point
    return -(-length // n)
