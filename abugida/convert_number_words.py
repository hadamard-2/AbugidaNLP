from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .number_words import amharic, parser


class NumberWordConverter:
    """
    A class to convert numbers to words for Amharic, Tigrinya and Afaan Oromoo.

    Attributes:
        languages (Tuple[str, ...]): The supported language codes.
        modes (Tuple[str, ...]): The supported conversion modes.
    """

    languages = ("am", "ti", "om")
    modes = ("cardinal", "ordinal", "ordinal_num", "year", "currency")

    def __init__(self):
        # Largest value (exclusive) each implemented language can write
        self.maxval = {"am": amharic.MAXVAL}
        self._modules = {"am": amharic}

    @staticmethod
    def _to_decimal(value) -> Decimal:
        """
        Turn a number or numeric string into a finite Decimal.

        Args:
            value (int|float|Decimal|str): The value. A float goes through its repr.

        Returns:
            Decimal: The finite value.

        Raises:
            TypeError: If the value is not an int, float, Decimal or str (bool is rejected).
            ValueError: If the value is a string that is not a number, or is NaN or infinite.
        """
        if isinstance(value, bool):
            raise TypeError("Value must be an int, float, Decimal or str, not bool")
        if isinstance(value, int):
            return Decimal(value)
        if isinstance(value, float):
            number = Decimal(repr(value))
        elif isinstance(value, Decimal):
            number = value
        elif isinstance(value, str):
            try:
                number = Decimal(value.strip())
            except InvalidOperation:
                raise ValueError(f"Not a number: {value!r}") from None
        else:
            raise TypeError(f"Value must be an int, float, Decimal or str, not {type(value).__name__}")
        if not number.is_finite():
            raise ValueError(f"Value must be finite: {value!r}")
        return number

    @classmethod
    def _split_decimal(cls, value) -> tuple[bool, int, str]:
        """
        Split a number into its sign, integer part and fraction digits.

        Args:
            value (int|float|Decimal|str): The value. An integral value has no fraction digits,
                so "2.0" splits like 2. Any other fraction keeps all its digits, trailing zeros included.

        Returns:
            Tuple[bool, int, str]: (negative, integer part, fraction digits or "").

        Raises:
            TypeError: If the value type is not supported.
            ValueError: If the value is not a finite number.
        """
        number = cls._to_decimal(value)
        text = format(abs(number), "f")
        whole, _, fraction = text.partition(".")
        if not fraction.strip("0"):
            fraction = ""
        integer = int(whole)
        return number < 0 and (integer > 0 or bool(fraction)), integer, fraction

    def to_words(
        self,
        value: int | float | Decimal | str,
        language: str,
        to: str = "cardinal",
        currency: str | None = None,
        gender: str = "m",
    ) -> str:
        """
        Convert a number to words.

        A float is read through its repr, so 2.5 is exactly 2.5. A Decimal or numeric string
        whose value is a whole number is treated as an int ("2.0" is "ሁለት"). Fraction digits are
        read one by one. In the 'currency' mode the amount is rounded to two places, half up.

        Args:
            value (int|float|Decimal|str): The number to convert.
            language (str): The language code ('am', 'ti' or 'om').
            to (str): The mode: 'cardinal', 'ordinal', 'ordinal_num', 'year' or 'currency'.
            currency (str|None): The currency code, for the 'currency' mode.
            gender (str): 'm' or 'f', for languages with gendered ordinals.

        Returns:
            str: The number in words.

        Raises:
            ValueError: If the language, the mode or the currency is not supported, or the value
                is a string that is not a finite number.
            TypeError: If the value type is not supported, or an ordinal is asked for zero, a
                negative or a non-integer.
            OverflowError: If the value is at or above the largest value of the language.
            NotImplementedError: If the language is not implemented yet.
        """
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")
        if to not in self.modes:
            raise ValueError(f"Unsupported mode: {to}")
        if language not in self.maxval:
            raise NotImplementedError(f"Language not implemented yet: {language}")
        module = self._modules[language]
        maxval = self.maxval[language]
        number = self._to_decimal(value)
        # adjusted() is the exponent of the leading digit, so this never builds a huge int
        if number.adjusted() >= len(str(maxval)):
            raise OverflowError(f"Value must be below {maxval}")

        if to == "currency":
            return self._currency_words(number, module, currency, maxval)

        negative, integer, fraction = self._split_decimal(number)
        if integer >= maxval:
            raise OverflowError(f"Value must be below {maxval}")
        if to in ("ordinal", "ordinal_num"):
            if negative or fraction or integer < 1:
                raise TypeError("Ordinals need a positive integer")
            function = module.ordinal if to == "ordinal" else module.ordinal_num
            return function(integer, gender)
        words = [module.cardinal(integer)]
        if negative:
            words.insert(0, module.NEGATIVE)
        if fraction:
            words.append(module.POINT)
            words.extend(module.cardinal(int(digit)) for digit in fraction)
        return " ".join(words)

    def _currency_words(self, number: Decimal, module, code: str | None, maxval: int) -> str:
        """
        Write a money amount, rounded to two places half up, in a language's words.

        Args:
            number (Decimal): The amount.
            module: The language module, with NEGATIVE and currency().
            code (str|None): The currency code.
            maxval (int): The exclusive upper limit of the whole part.

        Returns:
            str: The amount in words.

        Raises:
            ValueError: If the currency code is not supported.
            OverflowError: If the rounded whole part is at or above maxval.
        """
        negative = number < 0
        rounded = abs(number).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        whole, cents = divmod(int(rounded * 100), 100)
        if whole >= maxval:
            raise OverflowError(f"Value must be below {maxval}")
        words = module.currency(whole, cents, code)
        if negative and (whole or cents):
            words = f"{module.NEGATIVE} {words}"
        return words

    def to_number(self, text: str, language: str, to: str = "cardinal") -> int | Decimal | tuple[Decimal, str]:
        """
        Convert number words to a number.

        The words are split on whitespace and read with the usual scale-grouping rule, so spelling
        variants and digits mixed with scale words ("3 ሚሊዮን") are accepted.

        Args:
            text (str): The words, for example "ሃያ አምስት".
            language (str): The language code ('am', 'ti' or 'om').
            to (str): What the words are: 'cardinal', 'ordinal', 'ordinal_num', 'year' or 'currency'.

        Returns:
            int|Decimal|Tuple[Decimal, str]: An int for a whole number, a Decimal when the words
                have a fraction, and (amount, currency code) for 'currency'. A phrase with only a
                sub-unit gets the first currency code of the language.

        Raises:
            ValueError: If the language or mode is not supported, or the words are not a number.
            TypeError: If text is not a string.
            OverflowError: If the number is at or above the largest value of the language.
            NotImplementedError: If the language is not implemented yet.
        """
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")
        if to not in self.modes:
            raise ValueError(f"Unsupported mode: {to}")
        if language not in self.maxval:
            raise NotImplementedError(f"Language not implemented yet: {language}")
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, not {type(text).__name__}")
        module = self._modules[language]
        maxval = self.maxval[language]
        tokens = text.split()
        if not tokens:
            raise ValueError("No number words to read")
        if to == "ordinal_num":
            if len(tokens) != 1:
                raise ValueError(f"Not a numeric ordinal: {text!r}")
            return self._checked(module.parse_ordinal_num(tokens[0]), maxval)
        items = [item for token in tokens for item in module.lex(token)]
        if to == "currency":
            return self._parse_currency(items, module, maxval)
        negative = items[0][0] == "neg"
        if negative:
            items = items[1:]
        if to == "ordinal":
            if not items or items[-1][0] != "ord":
                raise ValueError("An ordinal must end with an ordinal word")
            kind = "scale" if items[-1][1] >= 100 else "num"
            items = items[:-1] + [(kind, items[-1][1])]
            value = self._checked(parser.fold_multiplier_first(items), maxval)
            if negative or value < 1:
                raise ValueError("An ordinal must be positive")
            return value
        kinds = [kind for kind, _ in items]
        if "point" in kinds:
            split = kinds.index("point")
            whole = self._checked(parser.fold_multiplier_first(items[:split]), maxval)
            digits = items[split + 1 :]
            if not digits or any(kind != "num" or value != int(value) or not 0 <= value <= 9 for kind, value in digits):
                raise ValueError("Fraction digits must be single digits")
            number = Decimal(f"{whole}.{''.join(str(int(value)) for _, value in digits)}")
            return -number if negative else number
        value = self._checked(parser.fold_multiplier_first(items), maxval)
        return -value if negative else value

    @staticmethod
    def _checked(value: int, maxval: int) -> int:
        """Return value, or raise OverflowError when it is at or above maxval."""
        if value >= maxval:
            raise OverflowError(f"Value must be below {maxval}")
        return value

    def _parse_currency(self, items: list, module, maxval: int) -> tuple[Decimal, str]:
        """
        Read the items of a money amount.

        Args:
            items (List[Item]): The lexed items, optionally led by a negative word.
            module: The language module, with CURRENCY_CODES.
            maxval (int): The exclusive upper limit of the whole part.

        Returns:
            Tuple[Decimal, str]: The amount to two places and the currency code.

        Raises:
            ValueError: If the items are not a money amount.
            OverflowError: If the whole part is at or above maxval.
        """
        negative = bool(items) and items[0][0] == "neg"
        if negative:
            items = items[1:]
        kinds = [kind for kind, _ in items]
        if kinds.count("unit") > 1 or kinds.count("subunit") > 1 or "point" in kinds or "neg" in kinds:
            raise ValueError("Not a money amount")
        unit_at = kinds.index("unit") if "unit" in kinds else None
        sub_at = kinds.index("subunit") if "subunit" in kinds else None
        if unit_at is None and sub_at is None:
            raise ValueError("A money amount needs a currency word")
        if sub_at is not None and sub_at != len(items) - 1:
            raise ValueError("A sub-unit word must come last")
        if unit_at is not None and sub_at is not None and unit_at > sub_at:
            raise ValueError("The unit word must come before the sub-unit word")
        whole = cents = 0
        code_index = 0
        rest = items
        if unit_at is not None:
            whole = self._checked(parser.fold_multiplier_first(items[:unit_at]), maxval)
            code_index = items[unit_at][1]
            rest = items[unit_at + 1 :]
            if sub_at is not None and rest and rest[0][0] == "join":
                rest = rest[1:]
        if sub_at is not None:
            sub_items = rest[:-1]
            cents = parser.fold_multiplier_first(sub_items)
            if cents > 99:
                raise ValueError("Sub-units must be below 100")
        elif rest:
            raise ValueError("Unexpected words after the currency word")
        amount = Decimal(whole) + Decimal(cents) / 100
        amount = amount.quantize(Decimal("0.01"))
        return (-amount if negative else amount), module.CURRENCY_CODES[code_index]
