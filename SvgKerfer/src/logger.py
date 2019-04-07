
def error(*a, **aa):
    print("Error:", end=' ')
    print(*a, **aa)
    exit(1)

def warning(*a, **aa):
    print("Warning:", end=' ')
    print(*a, **aa)

