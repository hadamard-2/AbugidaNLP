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

    def to_words(
        self,
        value: int,
        language: str,
        to: str = "cardinal",
        currency: str | None = None,
        gender: str = "m",
    ) -> str:
        """
        Convert a number to words.

        Args:
            value (int): The number to convert.
            language (str): The language code ('am', 'ti' or 'om').
            to (str): The mode: 'cardinal', 'ordinal', 'ordinal_num', 'year' or 'currency'.
            currency (str|None): The currency code, for the 'currency' mode.
            gender (str): 'm' or 'f', for languages with gendered ordinals.

        Returns:
            str: The number in words.

        Raises:
            ValueError: If the language or the mode is not supported.
            OverflowError: If the value is at or above the largest value of the language.
            NotImplementedError: If the language or the mode is not implemented yet.
        """
        if language not in self.languages:
            raise ValueError(f"Unsupported language: {language}")
        if to not in self.modes:
            raise ValueError(f"Unsupported mode: {to}")
        if language not in self.maxval:
            raise NotImplementedError(f"Language not implemented yet: {language}")
        if to != "cardinal":
            raise NotImplementedError(f"Mode not implemented yet: {to}")
        if not isinstance(value, int) or isinstance(value, bool):
            raise NotImplementedError("Only int input is implemented yet")
        if value >= self.maxval[language]:
            raise OverflowError(f"Value must be below {self.maxval[language]}")
        if value < 0:
            raise NotImplementedError("Negative numbers are not implemented yet")
        return amharic.cardinal(value)
