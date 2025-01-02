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


def traceback_global(v, w, pointers):
    i, j = len(v), len(w)
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
        if i <= 0 and j <= 0:
            break
    return "".join(new_v[::-1]) + "\n" + "".join(new_w[::-1]), path


def global_alignment(v, w):
    """
    Returns the score of the maximum scoring alignment of the strings v and w, as well as the actual alignment as
    computed by traceback_global.

    :param: v
    :param: w
    :param: delta
    """
    M = [[0 for j in range(len(w) + 1)] for i in range(len(v) + 1)]
    pointers = [[ORIGIN for j in range(len(w) + 1)] for i in range(len(v) + 1)]
    score, alignment = None, None
    # YOUR CODE HERE
    # raise NotImplementedError()
    for j in range(len(w) + 1):
        for i in range(len(v) + 1):
            max_list = []
            if i == 0 and j == 0:
                max_list.append([0, ORIGIN])
            if i > 0:
                max_list.append([M[i - 1][j] + delta[v[i - 1]]["-"], UP])
            if j > 0:
                max_list.append([M[i][j - 1] + delta["-"][w[j - 1]], LEFT])
            if i > 0 and j > 0:
                max_list.append([M[i - 1][j - 1] + delta[v[i - 1]][w[j - 1]], TOPLEFT])
            max_list = sorted(max_list, reverse=True)
            M[i][j], pointers[i][j] = max_list[0]
    alignment, path = traceback_global(v, w, pointers)
    return M, alignment, path, M[len(v)][len(w)]