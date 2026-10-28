import re
from decimal import Decimal

from ..normalize_text import TextNormalizer
from . import components, tables
from .parser import Item

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


_NORMALIZER = TextNormalizer()
_DIGITS = re.compile(r"\d+(\.\d+)?")


def _normalize(word: str) -> str:
    """Normalize a word the same way for lexicon keys and input tokens."""
    return _NORMALIZER.normalize(word, "am")


def _build_lexicon() -> dict[str, Item]:
    """
    Build the word lookup from the Amharic tables.

    Keys go through the text normalizer, so spelling variants of one word share a key.

    Returns:
        Dict[str, Item]: Normalized word to item.

    Raises:
        ValueError: If two different words normalize to one key with different items.
    """
    table = tables.AM
    base: dict[str, Item] = {}
    for value, word in enumerate(table["digits"]):
        base[word] = ("num", value)
    base[table["teens_prefix"]] = ("num", 10)
    for value, word in table["tens"].items():
        base[word] = ("num", value)
    for value, word in table["scales"].items():
        base[word] = ("scale", value)
    base[table["negative"]] = ("neg", 0)
    base[table["point"]] = ("point", 0)
    base[table["currency_joiner"]] = ("join", 0)
    value_of = {word: item[1] for word, item in base.items() if item[0] in ("num", "scale")}
    for plain, ordinal_word in table["ordinal_last"].items():
        base[ordinal_word] = ("ord", value_of[plain])
    for index, (unit, subunit) in enumerate(table["currencies"].values()):
        base[unit] = ("unit", index)
        base.setdefault(subunit, ("subunit", index))
    for variant, canonical in table["accept"].items():
        base[variant] = base[canonical]
    lexicon: dict[str, Item] = {}
    for word, item in base.items():
        key = _normalize(word)
        if lexicon.setdefault(key, item) != item:
            raise ValueError(f"Conflicting Amharic lexicon entries for {key!r}")
    return lexicon


_LEXICON = _build_lexicon()
CURRENCY_CODES = tuple(tables.AM["currencies"])


def lex(token: str) -> list[Item]:
    """
    Read one Amharic token as number items.

    Args:
        token (str): A word or a digit string such as "3" or "1.5".

    Returns:
        List[Item]: The items the token stands for.

    Raises:
        ValueError: If the token is not a number word or a digit string.
    """
    if _DIGITS.fullmatch(token):
        return [("num", Decimal(token) if "." in token else int(token))]
    key = _normalize(token)
    if key not in _LEXICON:
        raise ValueError(f"Not an Amharic number word: {token!r}")
    return [_LEXICON[key]]


def parse_ordinal_num(token: str) -> int:
    """
    Read a numeric ordinal such as "3ኛ".

    Args:
        token (str): Digits followed by the suffix "ኛ".

    Returns:
        int: The number, at least 1.

    Raises:
        ValueError: If the token is not digits plus the suffix, or the number is 0.
    """
    match = re.fullmatch(r"(\d+)-?ኛ", token)
    if not match or int(match.group(1)) < 1:
        raise ValueError(f"Not an Amharic numeric ordinal: {token!r}")
    return int(match.group(1))
