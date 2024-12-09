import json
from typing import Dict


class ScriptConverter:
    """
    A class for transliteration between Ethiopic and Latin scripts.

    Attributes:
    ethiopic_latin_map (Dict[str, str]): Mapping from Ethiopic to Latin.
    latin_ethiopic_map (Dict[str, str]): Mapping from Latin to Ethiopic.
    """

    def __init__(self, mapping_file: str = "SERA_table.json"):
        """
        Initialize the ScriptConverter with mappings from a JSON file.

        Parameters:
        mapping_file (str): Path to the JSON file containing transliteration mappings.
                            Defaults to 'SERA_table.json'.
        """
        self.ethiopic_latin_map = self._load_mappings(mapping_file)
        self.latin_ethiopic_map = {v: k for k, v in self.ethiopic_latin_map.items()}

    @staticmethod
    def _load_mappings(file_path: str) -> Dict[str, str]:
        """
        Load transliteration mappings from a JSON file.

        Parameters:
        file_path (str): Path to the JSON file.

        Returns:
        Dict[str, str]: The mapping from Ethiopic to Latin.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def transliterate(self, word: str, direction: str) -> str:
        """
        Transliterate a word between Ethiopic and Latin scripts.

        Parameters:
        word (str): The word to be transliterated.
        direction (str): The direction of transliteration.
                         'fwd' - Transliterate from Ethiopic to Latin.
                         'bwd' - Transliterate from Latin to Ethiopic.

        Returns:
        str: The transliterated word.

        Raises:
        ValueError: If an invalid direction is provided or if the word contains invalid characters.
        """
        if direction not in ["fwd", "bwd"]:
            raise ValueError(
                "Invalid direction. Use 'fwd' for Ethiopic to Latin or 'bwd' for Latin to Ethiopic."
            )

        if direction == "fwd":
            return self._ethiopic_to_latin(word)
        elif direction == "bwd":
            return self._latin_to_ethiopic(word)

    def _ethiopic_to_latin(self, word: str) -> str:
        """Transliterate a word from Ethiopic to Latin."""
        if not all(char in self.ethiopic_latin_map for char in word):
            raise ValueError("The word contains non-Ethiopic characters.")

        return "".join(self.ethiopic_latin_map[char] for char in word)

    def _latin_to_ethiopic(self, word: str) -> str:
        """Transliterate a word from Latin to Ethiopic."""
        ethiopic_word = ""
        i = min(4, len(word))
        while i > 0:
            if fidel := self.latin_ethiopic_map.get(word[:i]):
                ethiopic_word += fidel
                word = word[i:]
                i = min(4, len(word))
            else:
                i -= 1
                if i == 0:
                    raise ValueError(f"Invalid Latin sequence: '{word}'")

        return ethiopic_word
