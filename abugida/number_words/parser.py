from decimal import Decimal

Item = tuple[str, "int | Decimal"]


def fold_multiplier_first(items: list[Item]) -> int:
    """
    Fold number items written largest scale first, with the multiplier before its scale.

    Within a group below 1000 the part under 100 must strictly decrease: a tens word may be
    followed by a unit and nothing else. A scale of 100 takes a multiplier of 1 to 99. A scale of
    1000 or more takes the group before it, and must be smaller than every scale already applied.
    The one exception is a scale that stands alone after a finished total and is larger than the
    last scale applied: it multiplies the whole total ("አንድ ሺህ ሚሊዮን" is 10**9).

    A "num" value may be a Decimal when it came from a digit token such as "1.5". Such a value
    is allowed only directly before a scale of 1000 or more, and the product must be whole.

    Args:
        items (List[Item]): Items of kind "num" or "scale". The value of a "scale" is 100 or more.

    Returns:
        int: The folded value.

    Raises:
        ValueError: If the items are empty, of another kind, or in an invalid order.
    """
    if not items:
        raise ValueError("No number words to fold")
    total = 0
    group: int | Decimal = 0
    last_small = None
    last_scale = None  # scale applied to total most recently
    smallest_scale = None  # smallest scale applied to total so far
    scales_applied = 0  # how many scales >= 1000 have been applied to total
    for index, (kind, value) in enumerate(items):
        if kind == "num":
            if value < 0:
                raise ValueError("Negative digits are not allowed here")
            if value != int(value):
                following = items[index + 1] if index + 1 < len(items) else None
                if (
                    group != 0
                    or last_small is not None
                    or following is None
                    or following[0] != "scale"
                    or following[1] < 1000
                ):
                    raise ValueError(f"Fraction {value} is only allowed before a scale of 1000 or more")
            elif last_small is not None and not (
                10 <= last_small < 100 and 0 < value < 10 and last_small % 10 == 0
            ):
                raise ValueError(f"Number {value} cannot follow {last_small}")
            if value >= 100 and group != 0:
                raise ValueError(f"Number {value} cannot follow a partial group")
            if smallest_scale is not None and value >= smallest_scale:
                raise ValueError(f"Number {value} is not below the scale {smallest_scale}")
            group += value
            last_small = value
        elif kind == "scale":
            if value == 100:
                if group >= 100 or (group == 0 and last_small is not None) or group != int(group):
                    raise ValueError("Misplaced scale 100")
                group = (group or 1) * 100
                last_small = None
            elif value >= 1000:
                if last_small == 0:
                    raise ValueError("Zero cannot take a scale")
                # Which check handles which case: a lone larger scale multiplies the total only when the
                # total is a single scale group (scales_applied == 1); any other scale that is not
                # below the smallest applied one fails the ordering check right after it.
                if group == 0 and scales_applied == 1 and total > 0 and value > last_scale:
                    total *= value
                else:
                    if smallest_scale is not None and value >= smallest_scale:
                        raise ValueError(f"Scale {value} is not below the scale {smallest_scale}")
                    if group >= 1000:
                        raise ValueError(f"Group {group} is too large for scale {value}")
                    product = (group or 1) * value
                    if product != int(product):
                        raise ValueError(f"{group} times {value} is not a whole number")
                    total += int(product)
                group = 0
                last_small = None
                last_scale = value
                scales_applied += 1
                smallest_scale = value
            else:
                raise ValueError(f"Unsupported scale: {value}")
        else:
            raise ValueError(f"Cannot fold an item of kind {kind!r}")
    return total + int(group)


class _Reader:
    """A cursor over items that takes one item when it matches, optionally after a "join"."""

    def __init__(self, items: list[Item]):
        self.items = items
        self.pos = 0

    def done(self) -> bool:
        return self.pos == len(self.items)

    def take(self, kind: str, low: int, high: float, after_join: bool = False) -> int | None:
        """
        Take the next item if it is of the kind with a whole value in [low, high].

        Args:
            kind (str): The item kind to take.
            low (int): The smallest value to take.
            high (float): The largest value to take.
            after_join (bool): Whether a single "join" item may come first; it is taken too.

        Returns:
            int|None: The value taken, or None when nothing was taken.
        """
        pos = self.pos
        if after_join and pos < len(self.items) and self.items[pos][0] == "join":
            pos += 1
        if pos == len(self.items):
            return None
        item_kind, value = self.items[pos]
        if item_kind != kind or value != int(value) or not low <= value <= high:
            return None
        self.pos = pos + 1
        return int(value)


def _below_100(reader: _Reader, after_join: bool, multiplier: bool) -> int:
    """Read NUM, or TENS [join] DIGIT (no join in a multiplier). Return 0 when nothing is read."""
    value = reader.take("num", 1, 99, after_join)
    if value is None:
        return 0
    if value % 10 == 0:
        value += reader.take("num", 1, 9, after_join=not multiplier) or 0
    return value


def _below_1000(reader: _Reader, after_join: bool, multiplier: bool = False) -> int:
    """Read ["dhibba" [DIGIT]] [join] [below_100]. Return 0 when nothing is read."""
    hundreds = 0
    if reader.take("scale", 100, 100, after_join) is not None:
        hundreds = 100 * (reader.take("num", 1, 9) or 1)
    return hundreds + _below_100(reader, after_join or hundreds > 0, multiplier)


def fold_head_first(items: list[Item]) -> int:
    """
    Fold number items written scale word first, each scale followed by its multiplier.

    The grammar, read left to right and greedily ("join" is the word "and", DIGIT is 1 to 9 and
    TENS is 10, 20, ... 90)::

        number     := zero | group* [below_1000]           group scales strictly decrease
        group      := SCALE>=1000 [below_1000]             no multiplier means 1
        below_1000 := [100 [DIGIT]] [join] [below_100]     no DIGIT means 1
        below_100  := NUM | TENS [join] DIGIT              no join inside a multiplier

    One "join" may also come before every group but the first, and before the final part. A
    multiplier is the longest phrase that follows its scale, so "kuma dhibba shan" is 500 000.
    A "join" right after a scale word ends the multiplier before it starts, so the multiplier
    is 1: "kuma fi dhibba shan" is 1500 and "dhibba fi shan" is 105. Inside a multiplier a
    tens word takes its units only directly, so "kuma digdama fi tokko" is 20 001 (21 000 is
    "kuma digdamii tokko"), while "fi" after the hundreds stays part of the multiplier.

    Args:
        items (List[Item]): Items of kind "num", "scale" or "join".

    Returns:
        int: The folded value.

    Raises:
        ValueError: If the items are empty, of another kind, or do not follow the grammar.
    """
    if not items:
        raise ValueError("No number words to fold")
    if items == [("num", 0)]:
        return 0
    reader = _Reader(items)
    total = 0
    last_scale = None
    while not reader.done():
        after_join = last_scale is not None
        upper = last_scale - 1 if last_scale else float("inf")
        scale = reader.take("scale", 1000, upper, after_join)
        if scale is None:
            total += _below_1000(reader, after_join)
            break
        total += scale * (_below_1000(reader, after_join=False, multiplier=True) or 1)
        last_scale = scale
    if not reader.done():
        raise ValueError("Not a head-first number phrase")
    return total
