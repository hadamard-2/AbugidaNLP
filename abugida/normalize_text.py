from typing import Dict, List, Tuple


class TextNormalizer:
    """
    A class for merging Ethiopic letters that are pronounced the same, so that
    differently spelled forms of a word normalize to one spelling.

    Normalization runs in two steps per language:
        1. Family merges: a whole letter family is merged into another, form for form.
        2. Vowel merges: within a family, the 4th form is merged into the 1st (Amharic only).

    Both steps are composed into a single translation table per language, so every
    letter maps directly to its final form. See docs/normalization.md for the full table.

    Attributes:
        FAMILY_MERGES (Dict[str, List[Tuple[str, str]]]): Per language, pairs of
            (source letters, target letters), aligned letter by letter.
        VOWEL_MERGES (Dict[str, List[Tuple[str, str]]]): Per language, pairs of
            (4th-form letters, 1st-form letters), applied after the family merges.
    """

    _COMMON_FAMILY_MERGES = [
        ("ሐሑሒሓሔሕሖ", "ሀሁሂሃሄህሆ"),
        ("ኀኁኂኃኄኅኆ", "ሀሁሂሃሄህሆ"),
        ("ኋ", "ሗ"),
        ("ዐዑዒዓዔዕዖ", "አኡኢኣኤእኦ"),
        ("ሠሡሢሣሤሥሦሧ", "ሰሱሲሳሴስሶሷ"),
        ("ፀፁፂፃፄፅፆ", "ጸጹጺጻጼጽጾ"),
    ]

    FAMILY_MERGES = {
        "am": _COMMON_FAMILY_MERGES + [
            ("ኹኺኻኼኽኾ", "ሁሂሃሄህሆ"),
        ],
        "ti": _COMMON_FAMILY_MERGES + [
            ("ኸኹኺኻኼኽኾ", "ሀሁሂሃሄህሆ"),
            ("ዃ", "ሗ"),
            ("ኧ", "አ"),
            ("ቐቑቒቓቔቕቖቛ", "ቀቁቂቃቄቅቆቋ"),
        ],
    }

    VOWEL_MERGES = {
        "am": [("ሃኣ", "ሀአ")],
        "ti": [],
    }

    def __init__(self):
        self._tables = {
            language: self._build_table(
                self.FAMILY_MERGES[language], self.VOWEL_MERGES[language]
            )
            for language in self.FAMILY_MERGES
        }

    @staticmethod
    def _pairs_to_map(pairs: List[Tuple[str, str]]) -> Dict[str, str]:
        mapping = {}
        for sources, targets in pairs:
            if len(sources) != len(targets):
                raise ValueError(f"Unaligned merge: '{sources}' -> '{targets}'.")
            mapping.update(zip(sources, targets))
        return mapping

    @classmethod
    def _build_table(
        cls, family_merges: List[Tuple[str, str]], vowel_merges: List[Tuple[str, str]]
    ) -> Dict[int, str]:
        family_map = cls._pairs_to_map(family_merges)
        vowel_map = cls._pairs_to_map(vowel_merges)

        table = {}
        for letter in set(family_map) | set(vowel_map):
            merged = family_map.get(letter, letter)
            table[ord(letter)] = vowel_map.get(merged, merged)
        return table

    def normalize(self, text: str, language: str) -> str:
        """
        Normalize Ethiopic text by merging letters that are pronounced the same.

        Args:
            text (str): The text to normalize. Non-Ethiopic characters are left unchanged.
            language (str): The language whose rules to apply: "am" (Amharic) or "ti" (Tigrinya).

        Returns:
            str: The normalized text.

        Raises:
            ValueError: If the language is not supported.
        """
        if language not in self._tables:
            raise ValueError(
                f"Unsupported language '{language}'. Use 'am' for Amharic or 'ti' for Tigrinya."
            )

        return text.translate(self._tables[language])
