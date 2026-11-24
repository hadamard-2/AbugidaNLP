_SCALES = (10**12, 10**9, 10**6, 10**3, 100)


def components(n: int) -> list[tuple[int, int]]:
    """
    Split a non-negative integer into the components that are spoken in order.

    Scale groups and hundreds come out as ``(multiplier, scale)``. What is left below 100 comes
    out as ``(value, 1)``: a teen (11-19) in one piece, a tens value, then a units value. Zero is
    ``[(0, 1)]``.

    Args:
        n (int): The number to split, at least 0.

    Returns:
        List[Tuple[int, int]]: The components from the largest down.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("components() needs a non-negative integer")
    if n == 0:
        return [(0, 1)]
    parts: list[tuple[int, int]] = []
    for scale in _SCALES:
        group, n = divmod(n, scale)
        if group:
            parts.append((group, scale))
    if 11 <= n <= 19:
        parts.append((n, 1))
    else:
        tens, units = divmod(n, 10)
        if tens:
            parts.append((tens * 10, 1))
        if units:
            parts.append((units, 1))
    return parts
