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
                if group == 0 and total > 0 and last_scale is not None and value > last_scale:
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
                smallest_scale = value
            else:
                raise ValueError(f"Unsupported scale: {value}")
        else:
            raise ValueError(f"Cannot fold an item of kind {kind!r}")
    return total + int(group)
