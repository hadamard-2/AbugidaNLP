from . import components, tables

MAXVAL = 10**15


def cardinal(n: int) -> str:
    """
    Write a whole number as Amharic words, always with an explicit "አንድ" before a scale word.

    Args:
        n (int): The number to write, 0 <= n < 10**15.

    Returns:
        str: The number in words, separated by single spaces.

    Raises:
        ValueError: If n is negative.
        OverflowError: If n is 10**15 or more.
    """
    if n < 0:
        raise ValueError("cardinal() needs a non-negative integer")
    if n >= MAXVAL:
        raise OverflowError(f"number must be below {MAXVAL}")
    table = tables.AM
    words = []
    for value, scale in components(n):
        if scale > 1:
            words.append(cardinal(value))
            words.append(table["scales"][scale])
        elif value <= 10:
            words.append(table["digits"][value])
        elif value < 20:
            words.append(table["teens_prefix"])
            words.append(table["digits"][value - 10])
        else:
            words.append(table["tens"][value])
    return " ".join(words)
