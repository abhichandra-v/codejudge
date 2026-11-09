def title_case(s):
    return " ".join(word[0].upper() + word[1:].lower() for word in s.split())
