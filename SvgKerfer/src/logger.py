
def error(*a, fatal=True, **aa):
    print("Error:", end=' ')
    print(*a, **aa)
    if fatal:
        exit(1)

def warning(*a, **aa):
    print("Warning:", end=' ')
    print(*a, **aa)

