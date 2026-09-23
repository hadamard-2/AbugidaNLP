import re


class NumeralConverter:
    """
    A class to convert numerals between Ge'ez and Hindu-Arabic systems.

    Ge'ez numerals are written following CLDR's "%ethiopic" rule set (as used by ICU). A number
    is built from groups below 10,000 written with ፻, each followed by a run of ፼ marks. A run of
    k ፼ multiplies everything written since the previous run of more than k ፼, so 10^8 is ፼፼,
    123,456,789 is ፼፳፫፻፵፭፼፷፯፻፹፱ and 100,010,000 is ፼፩፼. A leading ፩ before ፻ or ፼ is
    omitted when formatting but accepted when parsing.

    Attributes:
        geez_arabic_map (Dict[str, int]): Mapping from Ge'ez to Arabic numerals.
        arabic_geez_map (Dict[int, str]): Mapping from Arabic to Ge'ez numerals.
    """

    def __init__(self):
        # Mapping between Ge'ez numerals and their Arabic equivalents
        self.geez_arabic_map = {
            "፩": 1,
            "፪": 2,
            "፫": 3,
            "፬": 4,
            "፭": 5,
            "፮": 6,
            "፯": 7,
            "፰": 8,
            "፱": 9,
            "፲": 10,
            "፳": 20,
            "፴": 30,
            "፵": 40,
            "፶": 50,
            "፷": 60,
            "፸": 70,
            "፹": 80,
            "፺": 90,
            "፻": 100,
            "፼": 10000,
        }
        self.arabic_geez_map = {
            value: key for key, value in self.geez_arabic_map.items()
        }

    def convert(self, num: int | str, from_numeral: str, to_numeral: str):
        """
        Convert a numeral between Ge'ez and Hindu-Arabic systems.

        Args:
            num (int|str): The numeral to be converted.
            from_numeral (str): Source numeral system ('gz' for Ge'ez, 'ha' for Hindu-Arabic).
            to_numeral (str): Target numeral system ('gz' for Ge'ez, 'ha' for Hindu-Arabic).

        Returns:
            str|int: The converted numeral.

        Raises:
            ValueError: If invalid numeral systems are provided or input format is incorrect.
        """
        if [from_numeral, to_numeral] not in [["gz", "ha"], ["ha", "gz"]]:
            raise ValueError(f"Unsupported conversion: {from_numeral} to {to_numeral}")

        if from_numeral == "gz":
            return self._convert_geez_to_arabic(num)
        if from_numeral == "ha":
            return self._convert_arabic_to_geez(num)

    def _convert_arabic_to_geez(self, arabic_num: int):
        if not isinstance(arabic_num, int):
            raise ValueError("Input must be an integer.")
        if arabic_num <= 0:
            raise ValueError("Ge'ez numerals do not support non-positive numbers.")

        return self._format_geez(arabic_num)

    def _convert_geez_to_arabic(self, geez_num: str):
        if not isinstance(geez_num, str):
            raise ValueError("Input must be a string representing a Ge'ez numeral.")
        if not geez_num:
            raise ValueError("Input must not be empty.")
        if not all(char in self.geez_arabic_map for char in geez_num):
            raise ValueError("Input contains invalid Ge'ez numeral characters.")

        arabic_num = self._parse_geez(geez_num)
        if self._strip_implicit_ones(geez_num) != self._strip_implicit_ones(
            self._format_geez(arabic_num)
        ):
            raise ValueError("Input is not a well-formed Ge'ez numeral.")
        return arabic_num

    def _format_geez(self, num: int, explicit_one: bool = False):
        if num < 10000:
            return self._format_geez_below_10000(num)
        level = 1
        while num >= 10000 ** (level + 1):
            level += 1
        head, rest = divmod(num, 10000**level)
        head_geez = "" if head == 1 and not explicit_one else self._format_geez(head)
        return head_geez + "፼" + self._format_geez_tail(rest, level - 1)

    def _format_geez_tail(self, num: int, level: int):
        # Formats the part of a number below 10000^(level + 1) that follows a ፼
        if level == 0:
            return self._format_geez(num) if num else ""
        if num < 10000**level:
            return "፼" * level + (self._format_geez(num, explicit_one=True) if num else "")
        head, rest = divmod(num, 10000**level)
        return self._format_geez(head) + "፼" + self._format_geez_tail(rest, level - 1)

    def _format_geez_below_10000(self, num: int):
        hundreds, rest = divmod(num, 100)
        geez_num = ""
        if hundreds:
            geez_num += ("" if hundreds == 1 else self._format_geez_below_100(hundreds)) + "፻"
        if rest:
            geez_num += self._format_geez_below_100(rest)
        return geez_num

    def _format_geez_below_100(self, num: int):
        tens, units = divmod(num, 10)
        return (self.arabic_geez_map[tens * 10] if tens else "") + (
            self.arabic_geez_map[units] if units else ""
        )

    def _parse_geez(self, geez_num: str):
        segments = []  # (፼ run length, value); run lengths strictly decrease
        group = 0  # value of the group below 10,000 being read
        coefficient = 0  # value of the digits read since the last ፻ or ፼
        i = 0
        while i < len(geez_num):
            char = geez_num[i]
            if char == "፻":
                group += (coefficient or 1) * 100
                coefficient = 0
                i += 1
            elif char == "፼":
                run = 0
                while i < len(geez_num) and geez_num[i] == "፼":
                    run += 1
                    i += 1
                value = group + coefficient or 1
                group = coefficient = 0
                while segments and segments[-1][0] <= run:
                    value += segments.pop()[1]
                segments.append((run, value * 10000**run))
            else:
                coefficient += self.geez_arabic_map[char]
                i += 1
        return sum(value for _, value in segments) + group + coefficient

    def _strip_implicit_ones(self, geez_num: str):
        # Drops a ፩ that stands alone before ፻ or ፼ (not the units digit of ፲፩ through ፺፩)
        return re.sub("(?<![፲-፺])፩(?=[፻፼])", "", geez_num)
