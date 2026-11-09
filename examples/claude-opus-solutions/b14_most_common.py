def most_common(items):
    counts = {}
    for x in items:
        counts[x] = counts.get(x, 0) + 1
    best, best_count = None, 0
    for x in items:
        if counts[x] > best_count:
            best, best_count = x, counts[x]
    return best
