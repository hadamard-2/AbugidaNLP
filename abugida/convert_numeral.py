class NumeralConverter:
    """
    A class to convert numerals between Ge'ez and Hindu-Arabic systems.

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

        arabic_segments = self._split_arabic_num(arabic_num)
        geez_num = ""
        for i in range(len(arabic_segments)):
            geez_num += self._arabic_to_geez_segment(
                arabic_segments[i], len(arabic_segments) - 1 - i
            )
        return geez_num

    def _convert_geez_to_arabic(self, geez_num: str):
        if not isinstance(geez_num, str):
            raise ValueError("Input must be a string representing a Ge'ez numeral.")
        if not geez_num:
            raise ValueError("Input must not be empty.")
        if not all(char in self.geez_arabic_map for char in geez_num):
            raise ValueError("Input contains invalid Ge'ez numeral characters.")

        arabic_segments = self._split_geez_num(geez_num)
        arabic_num = 0
        for i in range(len(arabic_segments)):
            arabic_num += arabic_segments[-i - 1] * pow(10, i * 2)
        return arabic_num

    def _split_arabic_num(self, arabic_num: int):
        arabic_num = str(arabic_num)
        segment_length = 2
        if len(arabic_num) % 2 == 1:
            arabic_num = "0" + arabic_num
        return [
            arabic_num[i : i + segment_length]
            for i in range(0, len(arabic_num), segment_length)
        ]

    def _arabic_to_geez_segment(self, arabic_segment: str, segment_index: int):
        if int(arabic_segment) == 0:
            return ""
        geez_segment = self.arabic_geez_map.get(int(arabic_segment))
        if not geez_segment:
            geez_segment = (
                self.arabic_geez_map[int(arabic_segment[0]) * 10]
                + self.arabic_geez_map[int(arabic_segment[1])]
            )
        if segment_index % 2 == 1:
            geez_segment = "፻" if geez_segment == "፩" else geez_segment + "፻"
        elif segment_index != 0:
            geez_segment = "፼" if geez_segment == "፩" else geez_segment + "፼"
        return geez_segment

    def _split_geez_num(self, geez_num: str):
        arabic_segments = []
        geez_num_len = len(geez_num)
        slice_end_index = geez_num_len
        for i in range(geez_num_len):
            if geez_num[-i - 1] == "፻":
                arabic_segments.insert(
                    0, self._geez_to_arabic_segment(geez_num[-i:slice_end_index])
                )
                slice_end_index = -i - 1
                if len(arabic_segments) % 2 == 0:
                    arabic_segments.insert(0, 0)
            elif geez_num[-i - 1] == "፼":
                arabic_segments.insert(
                    0, self._geez_to_arabic_segment(geez_num[-i:slice_end_index])
                )
                slice_end_index = -i - 1
                if len(arabic_segments) % 2 == 1:
                    arabic_segments.insert(0, 0)
        slice_end_index = geez_num.index("፻" if len(arabic_segments) % 2 == 1 else "፼")
        arabic_segments.insert(
            0, self._geez_to_arabic_segment(geez_num[0:slice_end_index])
        )
        return arabic_segments

    def _geez_to_arabic_segment(self, geez_num: str):
        if len(geez_num) == 0:
            return 1
        arabic_num = self.geez_arabic_map.get(geez_num)
        if not arabic_num:
            arabic_num = (
                self.geez_arabic_map[geez_num[0]] + self.geez_arabic_map[geez_num[1]]
            )
        return arabic_num
