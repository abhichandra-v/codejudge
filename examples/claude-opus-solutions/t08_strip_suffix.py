def remove_extension(filename):
    return filename[:-4] if filename.endswith(".txt") else filename
