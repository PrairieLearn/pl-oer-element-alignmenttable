keys = ["A", "C", "T", "G", "-"]
delta = {}
for i in range(len(keys)):
    delta[keys[i]] = {
        k: v
        for (k, v) in zip(
            keys, [1 if keys[i] == keys[j] else -1 for j in range(len(keys))]
        )
    }

UP = (-1, 0)
LEFT = (0, -1)
TOPLEFT = (-1, -1)
ORIGIN = (0, 0)


def traceback_fitting(v, w, init_j, pointers):
    """
    Returns the score of the maximum scoring alignment of short and all
    substrings of reference.
    
    :param: short the shorter of the two strings we are trying to align
    :param: reference the longer string among whose substrings we are doing global alignment
    :param: delta the scoring function for the alphabet of the two strings
    :param: init_j the starting index of the longer string
    
    :returns: a tuple (score, alignment)
    """
    i, j = len(v), init_j
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
        if i <= 0:
            break
    return "".join(new_v[::-1]) + "\n" + "".join(new_w[::-1]), path


def fitting_align(short, reference):
    """
    Returns the score of the maximum scoring alignment of short and all
    substrings of reference.

    :param: short the shorter of the two strings we are trying to align
    :param: reference the longer string among whose substrings we are doing global alignment
    :param: delta the scoring function for the alphabet of the two strings

    :returns: a tuple (score, alignment)
    """
    M = [[0 for j in range(len(reference) + 1)] for i in range(len(short) + 1)]
    pointers = [
        [ORIGIN for j in range(len(reference) + 1)] for i in range(len(short) + 1)
    ]
    score = None
    init_j = 0
    # YOUR CODE HERE
    # raise NotImplementedError()
    for j in range(len(reference) + 1):
        for i in range(len(short) + 1):
            max_list = []
            if i == 0:
                max_list.append([0, ORIGIN])
            if i > 0:
                max_list.append([M[i - 1][j] + delta[short[i - 1]]["-"], UP])
            if j > 0:
                max_list.append([M[i][j - 1] + delta["-"][reference[j - 1]], LEFT])
            if i > 0 and j > 0:
                max_list.append(
                    [M[i - 1][j - 1] + delta[short[i - 1]][reference[j - 1]], TOPLEFT]
                )
            max_list = sorted(max_list, reverse=True)
            M[i][j], pointers[i][j] = max_list[0]
    score_list = []
    for j in range(len(reference) + 1):
        score_list.append([M[len(short)][j], j])
    score_list = sorted(score_list, reverse=True)
    score, init_j = score_list[0]
    alignment, path = traceback_fitting(short, reference, init_j, pointers)
    return M, alignment, path, score