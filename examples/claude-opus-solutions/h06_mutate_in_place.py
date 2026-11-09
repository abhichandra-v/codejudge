def remove_evens(lst):
    lst[:] = [x for x in lst if x % 2 != 0]
