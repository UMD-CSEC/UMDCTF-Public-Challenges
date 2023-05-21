import itertools
from random import randint, shuffle
from dataclasses import dataclass
from z3 import *
from rich.progress import track

operations = ["*", ">>", "<<", "^", "+", "-"]
flag = "UMDCTF{h3r35_my_numb3r_50_c411_m3_m4yb3}"


def build_encoded_flag(operation: str, letter: str) -> tuple:
    # Declare integer constants a, b and c
    a = BitVec("a", 32)
    b = BitVec("b", 32)
    c = BitVec("c", 32)

    # Create a Z3 solver instance
    solver = Solver()

    c = BitVecVal(ord(letter), 32)

    # Add the constraints to the solver
    if operation == ">>":
        solver.add(a >> b == c)
    elif operation == "<<":
        solver.add(a << b == c)
    elif operation == "*":
        solver.add(a * b == c)
    elif operation == "^":
        solver.add(a ^ b == c, b > 5)
    elif operation == "+":
        solver.add(a + b == c, b > 6)
    elif operation == "-":
        solver.add(a - b == c, b > 18)

    # Check whether the solver is satisfiable
    if solver.check() == sat:
        # Get the model that satisfies the constraints
        model = solver.model()

        # Extract the values of a and b from the model
        a_value = model.eval(a).as_long()
        b_value = model.eval(b).as_long()

        """print(
            f"a = {a_value}, b = {b_value}, {chr(eval(f'{a_value} {operation} {b_value}'))}"
        )"""
        return (operation, a_value, b_value)
    else:
        build_encoded_flag(operations[randint(0, len(operations) - 1)], letter)


@dataclass
class Function:
    name: str
    arg1: str
    arg2: str
    op: str
    func_calls: list


def create_function_objects() -> list:
    functions = function_name_generator()
    to_return = []

    # Create array of function objects skipping the first one so that we can construct that afterwards
    for name in track(functions[1:]):
        to_return.append(
            Function(
                name,
                randint(0, 2147),
                randint(0, 127),
                operations[randint(0, len(operations) - 1)],
                get_random_entries_from_perms(
                    randint(1, len(functions) - 1), functions
                ),
            )
        )

    encoded_flag = [
        build_encoded_flag(operations[randint(0, len(operations) - 1)], i) for i in flag
    ]

    custom = []
    #print(encoded_flag)
    for i in encoded_flag:
        for j in to_return:
            if j.op == i[0]:
                custom.append(f"{j.name}({i[1]},{i[2]}); // a = {i[1]}, b = {i[2]}, {chr(eval(f'{i[1]} {i[0]} {i[2]}'))}")
                break

    print("\n\t".join(custom))
    print("return 0;\n}")
    return to_return


def get_random_entries_from_perms(iterations: int, rand: list):
    return [rand[randint(0, len(rand) - 1)] for _ in range(iterations)]


def function_name_generator() -> list:
    # s = "abcdefghi"
    s = "cdefghjk"#"cdefghjkl"

    # generate all permutations
    # perms = itertools.combinations_with_replacement(s, )

    to_return = [
        "".join(perm)
        for r in range(1, len(s) - 1)
        for perm in itertools.permutations(s, r)
    ]

    # print the permutations
    # to_return = ["".join(p) for p in perms]
    # print(to_return)
    return to_return


def build_func_string(curr: str, func_list: list) -> str:
    return "\t\t".join(
        [
            f"{func.name}({func.arg1},{func.arg2});\n"
            for func in func_list
            if func != curr
        ]
    )


def generate_code(filename: str):
    function_name = create_function_objects()  # = function_name_generator()
    shuffle(function_name)

    with open(filename, "w") as f:
        for i, name in enumerate(function_name, 1):
            function_call_string = f"""
            int {name.name}(int a, int b) {{
            \t{build_func_string(name, get_random_entries_from_perms(randint(1, 37), function_name))}
            \treturn a {name.op} b;
            }}
            """
            #print(function_call_string)
            f.write(function_call_string)


# create_function_objects()
# calc_flag()
print(
    """
#include <stdio.h>

int main(int argc, char** argv) {
    printf("Hello world!");
    return 0;
}

int a(int a, int b) {
"""
)
generate_code("test2.c")
# test = function_name_generator()
# print(get_random_entries_from_perms(8, test))
