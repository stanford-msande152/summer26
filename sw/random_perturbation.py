# random_perturbation.py
# Created: 2026-07-21
# AI model: MiniMax-M3
#
# A python expression that generates a random perturbation of integers from 1 to n.
# A "perturbation" here means a random reordering (permutation) of the sequence
# 1, 2, ..., n. Each integer in 1..n appears exactly once in the result.

import random


def random_perturbation(n: int, seed: int | None = None) -> list[int]:
    """Return a random permutation of the integers 1, 2, ..., n.

    Parameters
    ----------
    n : int
        Upper bound (inclusive). Must be a non-negative integer.
    seed : int | None
        Optional seed for the random number generator, useful for
        reproducible perturbations.

    Returns
    -------
    list[int]
        A list containing each integer from 1 to n exactly once, in a
        random order.

    Raises
    ------
    ValueError
        If n is negative.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    rng = random.Random(seed)  # isolated RNG so we don't affect global state
    return rng.sample(range(1, n + 1), n)


# ----------------------------------------------------------------------
# The single python expression that does the work
# ----------------------------------------------------------------------
# A random perturbation of integers from 1 to n can be written as one
# expression using random.sample:
#
#     random.sample(range(1, n + 1), n)
#
# Example usage:
#     n = 10
#     perturbed = random.sample(range(1, n + 1), n)
#     # e.g. -> [3, 7, 1, 10, 4, 2, 8, 5, 9, 6]
#
# If you want a reproducible perturbation, seed the module first:
#     random.seed(42)
#     perturbed = random.sample(range(1, n + 1), n)


if __name__ == "__main__":
    # Demo: print a few perturbations for several values of n.
    for n in (1, 5, 10, 20):
        print(f"n = {n:>2} -> {random_perturbation(n, seed=42)}")
