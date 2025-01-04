UP = (-1, 0)
LEFT = (0, -1)
TOPLEFT = (-1, -1)
ORIGIN = (0, 0)

def traceback_local(v, w, M, init_i, init_j, pointers):
    i, j = init_i, init_j
    new_v = []
    new_w = []
    path = [(i, j)]
    while True:
        di, dj = pointers[i][j]
        if (di, dj) == LEFT:
            new_v.append("-")
            new_w.append(w[j - 1])
        elif (di, dj) == UP:
            new_v.append(v[i - 1])
            new_w.append("-")
        elif (di, dj) == TOPLEFT:
            new_v.append(v[i - 1])
            new_w.append(w[j - 1])
        i, j = i + di, j + dj
        path.append((i, j))
        if M[i][j] == 0:
            break
    return "".join(new_v[::-1]) + "\n" + "".join(new_w[::-1]), path


def local_align(v, w, alphabet = ["A", "C", "T", "G"]):
    """
    Returns the score of the maximum scoring alignment of all possible substrings of v and w.

    :param: v The shorter of the two strings we are trying to align
    :param: w The longer string among whose substrings we are doing global alignment
    :param: alphabet Alphabet to use for generating the scoring function for the two strings

    :returns: a tuple (M, alignment, path, score)
    """
    alphabet.append("-")
    delta = {}
    for i in range(len(alphabet)):
        delta[alphabet[i]] = {
            k: v
            for (k, v) in zip(
                alphabet, [1 if alphabet[i] == alphabet[j] else -1 for j in range(len(alphabet))]
            )
        }

    M = [[0 for j in range(len(w) + 1)] for i in range(len(v) + 1)]
    pointers = [[ORIGIN for j in range(len(w) + 1)] for i in range(len(v) + 1)]
    score = None
    init_i, init_j = 0, 0

    for j in range(len(w) + 1):
        for i in range(len(v) + 1):
            max_list = []
            max_list.append([0, ORIGIN])
            if i > 0:
                max_list.append([M[i - 1][j] + delta[v[i - 1]]["-"], UP])
            if j > 0:
                max_list.append([M[i][j - 1] + delta["-"][w[j - 1]], LEFT])
            if i > 0 and j > 0:
                max_list.append([M[i - 1][j - 1] + delta[v[i - 1]][w[j - 1]], TOPLEFT])
            max_list = sorted(max_list, reverse=True)
            M[i][j], pointers[i][j] = max_list[0]
    score_list = []
    for j in range(len(w) + 1):
        for i in range(len(v) + 1):
            score_list.append([M[i][j], [i, j]])
    score_list = sorted(score_list, reverse=True)
    score, [init_i, init_j] = score_list[0]
    alignment, path = traceback_local(v, w, M, init_i, init_j, pointers)
    return M, alignment, path, score