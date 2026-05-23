"""Round timing schedule for the Choppediver OA."""
from __future__ import annotations

ROUND_BUDGETS_MS: list[int] = [
    8000,   # 1
    5000,   # 2
    3000,   # 3
    2000,   # 4
    1500,   # 5
    1000,   # 6
    750,    # 7
    500,    # 8
    350,    # 9
    250,    # 10
    150,    # 11
    80,     # 12
    40,     # 13
    15,     # 14
    5,      # 15
    5,      # 16
    5,      # 17
    5,      # 18
    5,      # 19
    5,      # 20
    5,      # 21
    5,      # 22
    5,      # 23
    5,      # 24
    5,      # 25
]

TOTAL_ROUNDS: int = len(ROUND_BUDGETS_MS)
