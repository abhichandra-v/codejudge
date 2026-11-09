import unicodedata


def normalized_equal(a, b):
    return unicodedata.normalize("NFC", a) == unicodedata.normalize("NFC", b)
