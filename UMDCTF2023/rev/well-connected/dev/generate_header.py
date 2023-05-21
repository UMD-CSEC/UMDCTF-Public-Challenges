import itertools


def function_name_generator() -> list:
    # s = "abcdefghi"
    s = "cdefghjk"

    # generate all permutations
    # perms = itertools.combinations_with_replacement(s, )

    to_return = [
        "".join(perm)
        for r in range(1, len(s) - 1)
        for perm in itertools.permutations(s, r)
    ]

    # print the permutations
    # to_return = ["".join(p) for p in perms]
    with open("final.h", "w") as f:
        for i in to_return:
            f.write(f"int {i}(int a, int b);")


function_name_generator()
