from . import components, tables

MAXVAL = 10**12
NEGATIVE = tables.OM["negative"]
POINT = tables.OM["point"]
ZERO = tables.OM["digits"][0]

_VOWELS = "aeiou"


def cardinal(n: int) -> str:
    """
    Write a whole number as Afaan Oromoo words, scale word first, with an explicit "tokko".

    Each scale group is the scale word and its multiplier ("kuma lama"). Tens and units are one
    component ("digdamii shan"). "fi" goes only before the last component.

    Args:
        n (int): The number to write, 0 <= n < 10**12.

    Returns:
        str: The number in words, separated by single spaces.

    Raises:
        ValueError: If n is negative.
        OverflowError: If n is 10**12 or more.
    """
    if n < 0:
        raise ValueError("cardinal() needs a non-negative integer")
    if n >= MAXVAL:
        raise OverflowError(f"number must be below {MAXVAL}")
    table = tables.OM
    parts: list[str] = []
    pending_tens = 0
    for value, scale in components(n):
        if scale > 1:
            parts.append(f"{table['scales'][scale]} {cardinal(value)}")
        elif value >= 20 and value % 10 == 0:
            # A tens word waits to see if a units word follows it
            pending_tens = value
        elif pending_tens:
            parts.append(f"{table['tens_linked'][pending_tens]} {table['digits'][value]}")
            pending_tens = 0
        elif value < 11:
            parts.append(table["digits"][value])
        else:
            parts.append(f"{table['teens_prefix']} {table['digits'][value - 10]}")
    if pending_tens:
        parts.append(table["tens"][pending_tens])
    if len(parts) > 1:
        parts[-1] = f"{table['conjunction']} {parts[-1]}"
    return " ".join(parts)


def ordinal(n: int, gender: str = "m") -> str:
    """
    Write a positive whole number as an Afaan Oromoo ordinal.

    The last word of the cardinal turns into its ordinal: an entry of the irregular table if it
    has one, otherwise "ffaa" after a vowel or "affaa" after a consonant.

    Args:
        n (int): The number, at least 1.
        gender (str): Ignored, Afaan Oromoo ordinals do not change with gender.

    Returns:
        str: The ordinal in words.

    Raises:
        TypeError: If n is not an integer, or is less than 1.
        OverflowError: If n is 10**12 or more.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal() needs a positive integer")
    table = tables.OM
    # A number that is exactly one scale (100, 10**3, ...) loses its "tokko" ("dhibbaffaa")
    words = [table["scales"][n]] if n in table["scales"] else cardinal(n).split(" ")
    last = words[-1]
    if last in table["ordinal_irregular"]:
        words[-1] = table["ordinal_irregular"][last]
    elif last[-1] in _VOWELS:
        words[-1] = last + table["ordinal_suffix"]
    else:
        words[-1] = last + table["ordinal_suffix_after_consonant"]
    return " ".join(words)


def ordinal_num(n: int, gender: str = "m") -> str:
    """
    Write a positive whole number as digits with the Afaan Oromoo ordinal suffix "ffaa".

    Args:
        n (int): The number, at least 1.
        gender (str): Ignored, Afaan Oromoo ordinals do not change with gender.

    Returns:
        str: The number in digits followed by "ffaa", for example "3ffaa".

    Raises:
        TypeError: If n is not an integer, or is less than 1.
        OverflowError: If n is 10**12 or more.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal_num() needs a positive integer")
    if n >= MAXVAL:
        raise OverflowError(f"number must be below {MAXVAL}")
    return f"{n}{tables.OM['ordinal_suffix']}"


def currency(whole: int, cents: int, code: str) -> str:
    """
    Write a money amount as Afaan Oromoo words, amount then unit.

    A zero whole part is left out when there are cents; a zero cents part is always left out.
    The two parts are separated by a space.

    Args:
        whole (int): The whole units, at least 0.
        cents (int): The sub-units, 0 to 99.
        code (str): The currency code, for example "ETB".

    Returns:
        str: The amount in words, "zeeroo" plus the unit when both parts are zero.

    Raises:
        ValueError: If the currency code is not supported, or cents are given for a currency
            that has no sub-unit word.
        OverflowError: If whole is 10**12 or more.
    """
    table = tables.OM
    if code not in table["currencies"]:
        raise ValueError(f"Unsupported currency: {code}")
    unit, subunit = table["currencies"][code]
    if cents > 0 and subunit is None:
        raise ValueError(f"Currency {code} has no sub-unit word")
    parts = []
    if whole > 0 or cents == 0:
        parts.append(f"{cardinal(whole)} {unit}")
    if cents > 0:
        parts.append(f"{cardinal(cents)} {subunit}")
    return " ".join(parts)
