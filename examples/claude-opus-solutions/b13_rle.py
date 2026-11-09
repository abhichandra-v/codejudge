def run_length_encode(s):
    if not s:
        return ""
    parts = []
    prev, count = s[0], 1
    for ch in s[1:]:
        if ch == prev:
            count += 1
        else:
            parts.append(f"{prev}{count}")
            prev, count = ch, 1
    parts.append(f"{prev}{count}")
    return "".join(parts)
