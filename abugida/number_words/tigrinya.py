from . import components, tables

MAXVAL = 10**12
NEGATIVE = tables.TI["negative"]
POINT = tables.TI["point"]
ZERO = tables.TI["digits"][0]


def _suffixed(word: str, scale: int = 1) -> str:
    """Attach the conjunction "ን" to the last word of a component (scale words use their stem)."""
    table = tables.TI
    if scale > 1 and scale in table["scales_suffixed"]:
        word = word[: -len(table["scales"][scale])] + table["scales_suffixed"][scale]
    return word + table["conjunction"]


def cardinal(n: int) -> str:
    """
    Write a whole number as Tigrinya words in the formal form.

    A number of one component (5, 20, 200, 5000) is written bare. A number of several components
    puts "ን" on the last word of every component. A teen is one block with "ን" only on its last
    word. A scale word never takes "ሓደ" before it.

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
    table = tables.TI
    parts = components(n)
    joined = len(parts) > 1
    chunks = []
    for value, scale in parts:
        if scale > 1:
            scale_word = table["scales"][scale]
            if joined:
                scale_word = _suffixed(scale_word, scale)
            words = scale_word if value == 1 else f"{cardinal(value)} {scale_word}"
        elif value <= 10:
            words = table["digits"][value]
            if joined:
                words = _suffixed(words)
        elif value < 20:
            words = f"{table['teens_prefix']} {table['digits'][value - 10]}"
            if joined:
                words = _suffixed(words)
        else:
            words = table["tens"][value]
            if joined:
                words = _suffixed(words)
        chunks.append(words)
    return " ".join(chunks)


def ordinal(n: int, gender: str = "m") -> str:
    """
    Write a positive whole number as a Tigrinya ordinal.

    1 to 10 are dedicated words, masculine or feminine. From 11 up it is "መበል" plus the cardinal.

    Args:
        n (int): The number, at least 1.
        gender (str): "m" (default) or "f".

    Returns:
        str: The ordinal in words.

    Raises:
        TypeError: If n is not an integer, or is less than 1.
        OverflowError: If n is 10**12 or more.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal() needs a positive integer")
    if n >= MAXVAL:
        raise OverflowError(f"number must be below {MAXVAL}")
    table = tables.TI
    if n <= 10:
        return table["ordinals_1_10"][n][gender == "f"]
    return f"{table['ordinal_prefix']} {cardinal(n)}"


def ordinal_num(n: int, gender: str = "m") -> str:
    """
    Write a positive whole number as a numeric Tigrinya ordinal.

    1 to 10 are the digits plus "ይ" ("ይቲ" feminine). From 11 up it is "መበል" plus the digits.

    Args:
        n (int): The number, at least 1.
        gender (str): "m" (default) or "f".

    Returns:
        str: For example "3ይ", "3ይቲ" or "መበል 11".

    Raises:
        TypeError: If n is not an integer, or is less than 1.
        OverflowError: If n is 10**12 or more.
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal_num() needs a positive integer")
    if n >= MAXVAL:
        raise OverflowError(f"number must be below {MAXVAL}")
    table = tables.TI
    if n <= 10:
        return f"{n}{table['ordinal_num_suffix'][gender == 'f']}"
    return f"{table['ordinal_prefix']} {n}"


def currency(whole: int, cents: int, code: str) -> str:
    """
    Write a money amount as Tigrinya words.

    The parts are amount, unit word, sub-amount, sub-unit word, side by side. A zero whole part is
    left out when there are cents; a zero cents part is always left out.

    Args:
        whole (int): The whole units, at least 0.
        cents (int): The sub-units, 0 to 99.
        code (str): The currency code, for example "ETB".

    Returns:
        str: The amount in words, "ባዶ" plus the unit when both parts are zero.

    Raises:
        ValueError: If the currency code is not supported.
        OverflowError: If whole is 10**12 or more.
    """
    table = tables.TI
    if code not in table["currencies"]:
        raise ValueError(f"Unsupported currency: {code}")
    unit, subunit = table["currencies"][code]
    parts = []
    if whole > 0 or cents == 0:
        parts.append(f"{cardinal(whole)} {unit}")
    if cents > 0:
        parts.append(f"{cardinal(cents)} {subunit}")
    joiner = f" {table['currency_joiner']} " if table["currency_joiner"] else " "
    return joiner.join(parts)
