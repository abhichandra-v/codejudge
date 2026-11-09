def is_anagram(a, b):
    def letters(s):
        return sorted(ch for ch in s.lower() if ch.isalpha())

    return letters(a) == letters(b)
