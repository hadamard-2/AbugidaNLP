from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from .number_words import amharic


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
