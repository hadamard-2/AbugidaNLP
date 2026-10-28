import re

from . import components, parser, tables
from .parser import Item

MAXVAL = 10**12
NEGATIVE = tables.OM["negative"]
POINT = tables.OM["point"]
ZERO = tables.OM["digits"][0]

_VOWELS = "aeiou"


def cardinal(n: int) -> str:
    """
    Write a whole number as Afaan Oromoo words, scale word first, with an explicit "tokko".

    Each scale group is the scale word and its multiplier ("kuma lama"). A group of 100 or more
    that is not exact hundreds repeats the scale word for its hundreds and for the rest
    ("kuma dhibba tokko fi kuma digdamii shan" is 125 000). Tens and units are one component
    ("digdamii shan"), and "fi" goes between every two components.

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
            scale_word = table["scales"][scale]
            rest = value % 100 if value > 100 else 0
            for piece in (value - rest, rest):
                if piece:
                    parts.append(f"{scale_word} {cardinal(piece)}")
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
    return f" {table['conjunction']} ".join(parts)


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
    words[-1] = _ordinal_word(words[-1])
    return " ".join(words)


def _ordinal_word(word: str) -> str:
    """Turn one cardinal word into its ordinal: the irregular entry, else "ffaa" or "affaa"."""
    table = tables.OM
    if word in table["ordinal_irregular"]:
        return table["ordinal_irregular"][word]
    if word[-1] in _VOWELS:
        return word + table["ordinal_suffix"]
    return word + table["ordinal_suffix_after_consonant"]


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


def _build_lexicon() -> dict[str, Item]:
    """
    Build the word lookup from the Afaan Oromoo tables.

    Every digit, tens and scale word also gets its ordinal form ("lamaffaa", "dhibbaffaa") as an "ord" item.

    Returns:
        Dict[str, Item]: Lowercase word to item.

    Raises:
        ValueError: If an accepted variant is a word of its own, or two words share a key
            with different items.
    """
    table = tables.OM
    base: dict[str, Item] = {}
    words = [(word, ("num", value)) for value, word in enumerate(table["digits"])]
    words += [(word, ("num", value)) for value, word in table["tens"].items()]
    words += [(word, ("scale", value)) for value, word in table["scales"].items()]
    for word, (kind, value) in words:
        base[word] = (kind, value)
        if value > 0:
            base[_ordinal_word(word)] = ("ord", value)
    base[table["teens_prefix"]] = ("num", 10)
    for value, word in table["tens_linked"].items():
        base[word] = ("num", value)
    base[table["conjunction"]] = ("join", 0)
    base[table["year_prefix"]] = ("yskip", 0)
    base[table["negative"]] = ("neg", 0)
    base[table["point"]] = ("point", 0)
    for index, (unit, subunit) in enumerate(table["currencies"].values()):
        base[unit] = ("unit", index)
        if subunit is not None:
            # A sub-unit word shared by currencies names the first of them
            base.setdefault(subunit, ("subunit", index))
    for accept in (table["accept"], table["ordinal_accept"]):
        for variant, canonical in accept.items():
            if variant != canonical and variant in base:
                raise ValueError(f"Accepted variant {variant!r} is already a word of its own")
            base[variant] = base[canonical]
    lexicon: dict[str, Item] = {}
    for word, item in base.items():
        if lexicon.setdefault(word.lower(), item) != item:
            raise ValueError(f"Conflicting Afaan Oromoo lexicon entries for {word.lower()!r}")
    return lexicon


_LEXICON = _build_lexicon()
CURRENCY_CODES = tuple(tables.OM["currencies"])
# The unit word may also come first ("qarshii shantama")
CURRENCY_UNIT_FIRST = True


def lex(token: str) -> list[Item]:
    """
    Read one Afaan Oromoo token as number items.

    The token is lowercased and a trailing comma dropped. "fi" is a "join" item, which the
    head-first reading uses to end a multiplier. A word not in the lexicon is tried again
    without a doubled final vowel ("tokkoo" is "tokko"), and a teen written as one word
    ("kudhatokko", "kudha-tokko") is split after "kudha". "bara" is a "yskip" item, which only
    the year mode ignores.

    Args:
        token (str): A word.

    Returns:
        List[Item]: The items the token stands for.

    Raises:
        ValueError: If the token is not a number word.
    """
    word = token.lower().removesuffix(",")
    if word in _LEXICON:
        return [_LEXICON[word]]
    if len(word) > 2 and word[-1] in _VOWELS and word[-1] == word[-2] and word[:-1] in _LEXICON:
        return [_LEXICON[word[:-1]]]
    prefix = tables.OM["teens_prefix"]
    rest = word.removeprefix(prefix).removeprefix("-")
    if word.startswith(prefix) and rest in _LEXICON:
        return [_LEXICON[prefix], _LEXICON[rest]]
    raise ValueError(f"Not an Afaan Oromoo number word: {token!r}")


def fold(items: list[Item], year: bool = False) -> int:
    """
    Fold number items, reading the scale-word-first order before the reversed one.

    The head-first reading is tried first, so the default reading always wins. Only when it
    fails is the multiplier-first order ("lama kuma") tried. In year mode, two numbers below
    100 with the first at least 10 are also read as a year ("digdamii kudha shan" is 2015).

    Args:
        items (List[Item]): Items of kind "num", "scale" or "join".
        year (bool): Whether the two-part year form is allowed.

    Returns:
        int: The folded value.

    Raises:
        ValueError: If no reading fits.
    """
    if not items:
        raise ValueError("No number words to fold")
    try:
        return parser.fold_head_first(items)
    except ValueError:
        pass
    if year:
        try:
            return _two_part_year(items)
        except ValueError:
            pass
    return _reversed_order(items)


def _reversed_order(items: list[Item]) -> int:
    """Read the multiplier-first order ("lama kuma"), with single joins only between words."""
    kinds = [kind for kind, _ in items]
    if "join" in (kinds[0], kinds[-1]) or any(a == b == "join" for a, b in zip(kinds, kinds[1:])):
        raise ValueError("A conjunction must stand alone between two number words")
    if len(items) > 1 and ("num", 0) in items:
        raise ValueError("Zero cannot be part of a larger number")
    return parser.fold_multiplier_first([item for item in items if item[0] != "join"])


def _two_part_year(items: list[Item]) -> int:
    """Read two numbers below 100, the first at least 10, as first * 100 + second."""
    if any(kind not in ("num", "join") for kind, _ in items):
        raise ValueError("A two-part year has no scale words")
    # The longest first part comes first, like the greedy head-first reading
    for split in range(len(items) - 1, 0, -1):
        try:
            century, rest = parser.fold_head_first(items[:split]), parser.fold_head_first(items[split:])
        except ValueError:
            continue
        if 10 <= century and rest >= 1:
            return century * 100 + rest
    raise ValueError("Not a two-part year")


def parse_ordinal_num(text: str) -> int:
    """
    Read a numeric ordinal such as "3ffaa" or "3-ffaa".

    Args:
        text (str): Digits plus the suffix "ffaa".

    Returns:
        int: The number, at least 1.

    Raises:
        ValueError: If the text is not a numeric ordinal, or the number is 0.
    """
    suffix = re.escape(tables.OM["ordinal_suffix"])
    match = re.fullmatch(rf"(\d+)-?{suffix}", text.strip().lower())
    number = int(match.group(1)) if match else 0
    if number < 1:
        raise ValueError(f"Not an Afaan Oromoo numeric ordinal: {text!r}")
    return number
