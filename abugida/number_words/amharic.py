from . import components, tables

MAXVAL = 10**15
NEGATIVE = tables.AM["negative"]
POINT = tables.AM["point"]
ZERO = tables.AM["digits"][0]


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


def ordinal(n: int, gender: str = "m") -> str:
    """
    Write a positive whole number as an Amharic ordinal.

    A number that is exactly one scale (100, 10**3, 10**6, 10**9, 10**12) loses its "አንድ" and
    becomes the bare scale ordinal ("መቶኛ"). Any other number is its cardinal with the last word
    turned into its ordinal form.

    Args:
        n (int): The number, at least 1.
        gender (str): Ignored, Amharic ordinals do not change with gender.

    Returns:
        str: The ordinal in words.

    Raises:
        TypeError: If n is not an integer, or is less than 1.
        OverflowError: If n is 10**15 or more.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal() needs a positive integer")
    table = tables.AM
    if n in table["scales"]:
        return table["ordinal_last"][table["scales"][n]]
    words = cardinal(n).split(" ")
    words[-1] = table["ordinal_last"][words[-1]]
    return " ".join(words)


def ordinal_num(n: int, gender: str = "m") -> str:
    """
    Write a positive whole number as digits with the Amharic ordinal suffix "ኛ".

    Args:
        n (int): The number, at least 1.
        gender (str): Ignored, Amharic ordinals do not change with gender.

    Returns:
        str: The number in digits followed by "ኛ", for example "3ኛ".

    Raises:
        TypeError: If n is not an integer, or is less than 1.
        OverflowError: If n is 10**15 or more.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal_num() needs a positive integer")
    if n >= MAXVAL:
        raise OverflowError(f"number must be below {MAXVAL}")
    return f"{n}ኛ"


def currency(whole: int, cents: int, code: str) -> str:
    """
    Write a money amount as Amharic words.

    A zero whole part is left out when there are cents; a zero cents part is always left out.
    When both parts are written, they are joined with "ከ".

    Args:
        whole (int): The whole units, at least 0.
        cents (int): The sub-units, 0 to 99.
        code (str): The currency code, for example "ETB".

    Returns:
        str: The amount in words, "ዜሮ" plus the unit when both parts are zero.

    Raises:
        ValueError: If the currency code is not supported.
        OverflowError: If whole is 10**15 or more.
    """
    table = tables.AM
    if code not in table["currencies"]:
        raise ValueError(f"Unsupported currency: {code}")
    unit, subunit = table["currencies"][code]
    parts = []
    if whole > 0 or cents == 0:
        parts.append(f"{cardinal(whole)} {unit}")
    if cents > 0:
        parts.append(f"{cardinal(cents)} {subunit}")
    return f" {table['currency_joiner']} ".join(parts)
