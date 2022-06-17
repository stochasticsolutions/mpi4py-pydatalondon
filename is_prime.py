import math

def is_prime(N):
    n = int(math.sqrt(N))  + 1
    if N < 5:
        return N in (2, 3)
    if N % 2 == 0:
        return False
    for i in range(3, n, 2):
        if N % i == 0:
            return False
    return True

print(' '.join(str(n) for n in range(1, 100) if is_prime(n)))
