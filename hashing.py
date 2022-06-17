import hashlib
import time


def hash_it(n):
    return hashlib.sha512(str(n).encode('ascii')).hexdigest()


def string_index_sort_hashes(numbers):
    sorted_hashes = sorted((hash_it(s), i) for i, s in enumerate(numbers))
    return [i for (s, i) in sorted_hashes]


if __name__ == '__main__':
    N = 10_000_000
    t0 = time.time()
    string_index_sort_hashes(list(range(N)))
    t1 = time.time()
    print(f'Time: {t1 - t0:.4f} seconds')
