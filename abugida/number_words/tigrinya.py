import re
from decimal import Decimal

from ..normalize_text import TextNormalizer
from . import components, tables
from .parser import Item

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


def cardinal(n: int, explicit_one: bool = True) -> str:
    """
    Write a whole number as Tigrinya words in the formal form.

    A number of one component (5, 20, 200, 5000) is written bare. A number of several components
    puts "ን" on the last word of every component. A teen is one block with "ን" only on its last
    word. A scale word has an explicit "ሓደ" before it for one ("ሓደ ሽሕ").

    Args:
        n (int): The number to write, 0 <= n < 10**12.
        explicit_one (bool): When False, a number from 100 to 199 leaves out its leading "ሓደ"
            ("ሚእትን ሓደን"). Larger numbers always keep it.

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
            words = f"{cardinal(value)} {scale_word}"
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
    if not explicit_one and 100 <= n < 200:
        chunks[0] = chunks[0].split(" ", 1)[1]
    return " ".join(chunks)


def ordinal(n: int, gender: str = "m", explicit_one: bool = True) -> str:
    """
    Write a positive whole number as a Tigrinya ordinal.

    1 to 10 are dedicated words, masculine or feminine. From 11 up it is "መበል" plus the cardinal.

    Args:
        n (int): The number, at least 1.
        gender (str): "m" (default) or "f".
        explicit_one (bool): Passed on to cardinal(), so False gives "መበል ሚእቲ" for 100.

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
    return f"{table['ordinal_prefix']} {cardinal(n, explicit_one)}"


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
    """
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise TypeError("ordinal_num() needs a positive integer")
    table = tables.TI
    if n <= 10:
        return f"{n}{table['ordinal_num_suffix'][gender == 'f']}"
    return f"{table['ordinal_prefix']} {n}"


def currency(whole: int, cents: int, code: str, explicit_one: bool = True) -> str:
    """
    Write a money amount as Tigrinya words.

    The parts are amount, unit word, sub-amount, sub-unit word, side by side. A zero whole part is
    left out when there are cents; a zero cents part is always left out.

    Args:
        whole (int): The whole units, at least 0.
        cents (int): The sub-units, 0 to 99.
        code (str): The currency code, for example "ETB".
        explicit_one (bool): Passed on to cardinal() for the whole units.

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
        parts.append(f"{cardinal(whole, explicit_one)} {unit}")
    if cents > 0:
        parts.append(f"{cardinal(cents)} {subunit}")
    joiner = f" {table['currency_joiner']} " if table["currency_joiner"] else " "
    return joiner.join(parts)


_NORMALIZER = TextNormalizer()
_DIGITS = re.compile(r"\d+(\.\d+)?")


def _normalize(word: str) -> str:
    """Normalize a word the same way for lexicon keys and input tokens."""
    return _NORMALIZER.normalize(word, "ti")


def _build_lexicon() -> dict[str, Item]:
    """
    Build the word lookup from the Tigrinya tables.

    Keys go through the text normalizer, so spelling variants of one word share a key.

    Returns:
        Dict[str, Item]: Normalized word to item.

    Raises:
        ValueError: If two different words normalize to one key with different items.
    """
    table = tables.TI
    base: dict[str, Item] = {}
    for value, word in enumerate(table["digits"]):
        base[word] = ("num", value)
    base[table["teens_prefix"]] = ("num", 10)
    for value, word in table["tens"].items():
        base[word] = ("num", value)
    for value, word in table["scales"].items():
        base[word] = ("scale", value)
    for value, word in table["scales_suffixed"].items():
        base[word] = ("scale", value)
    base[table["negative"]] = ("neg", 0)
    base[table["point"]] = ("point", 0)
    base[table["ordinal_prefix"]] = ("ordprefix", 0)
    for value, words in table["ordinals_1_10"].items():
        for word in words:
            base[word] = ("ordword", value)
    for word in table["currency_skip"]:
        base[word] = ("cskip", 0)
    for index, (unit, subunit) in enumerate(table["currencies"].values()):
        base[unit] = ("unit", index)
        base.setdefault(subunit, ("subunit", index))
    for variant, canonical in table["accept"].items():
        if variant in base:
            raise ValueError(f"Accepted variant {variant!r} is already a word of its own")
        base[variant] = base[canonical]
    lexicon: dict[str, Item] = {}
    for word, item in base.items():
        key = _normalize(word)
        if lexicon.setdefault(key, item) != item:
            raise ValueError(f"Conflicting Tigrinya lexicon entries for {key!r}")
    return lexicon


_LEXICON = _build_lexicon()
CURRENCY_CODES = tuple(tables.TI["currencies"])


def lex(token: str) -> list[Item]:
    """
    Read one Tigrinya token as number items.

    A lone "ን" is a "skip" item. A word that is not in the lexicon but ends in "ን" is looked up
    again without that "ን" ("ሚእትን" is "ሚእቲ"). The currency fillers ("ምስ", "ጥራይ", "ጥራሕ") come
    out as "cskip" items, which only the currency mode ignores.

    Args:
        token (str): A word or a digit string such as "3" or "1.5".

    Returns:
        List[Item]: The items the token stands for.

    Raises:
        ValueError: If the token is not a number word or a digit string.
    """
    conjunction = tables.TI["conjunction"]
    if _DIGITS.fullmatch(token):
        return [("num", Decimal(token) if "." in token else int(token))]
    if token == conjunction:
        return [("skip", 0)]
    key = _normalize(token)
    if key in _LEXICON:
        return [_LEXICON[key]]
    if token.endswith(conjunction):
        stripped = _normalize(token[: -len(conjunction)])
        if stripped in _LEXICON:
            return [_LEXICON[stripped]]
    raise ValueError(f"Not a Tigrinya number word: {token!r}")


def parse_ordinal_num(text: str) -> int:
    """
    Read a numeric ordinal such as "3ይ", "3ይቲ", "3-ይ" or "መበል 11".

    Args:
        text (str): Digits plus the suffix of either gender, or the prefix "መበል" and digits.

    Returns:
        int: The number, at least 1.

    Raises:
        ValueError: If the text is not a numeric ordinal, or the number is 0.
    """
    table = tables.TI
    suffixes = "|".join(sorted(map(re.escape, table["ordinal_num_suffix"]), key=len, reverse=True))
    prefix = re.escape(table["ordinal_prefix"])
    match = re.fullmatch(rf"(?:(\d+)-?(?:{suffixes})|{prefix}\s+(\d+))", text.strip())
    number = int(next(group for group in match.groups() if group)) if match else 0
    if number < 1:
        raise ValueError(f"Not a Tigrinya numeric ordinal: {text!r}")
    return number
