def add_int32(a, b):
    total = (a + b) & 0xFFFFFFFF
    return total - 0x100000000 if total & 0x80000000 else total
