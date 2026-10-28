import unittest
from abugida import TextNormalizer


class TestNormalizeAmharic(unittest.TestCase):
    def setUp(self):
        self.normalize = TextNormalizer().normalize

        self.test_cases = [
            # ሐ and ኀ families merge into ሀ, then the 4th form into the 1st
            ("ሐ", "ሀ"),
            ("ሑ", "ሁ"),
            ("ሓ", "ሀ"),
            ("ኀ", "ሀ"),
            ("ኆ", "ሆ"),
            ("ኃ", "ሀ"),
            ("ሃ", "ሀ"),
            ("ኋ", "ሗ"),
            # ኸ family joins ሀ, except ኸ itself
            ("ኹ", "ሁ"),
            ("ኻ", "ሀ"),
            ("ኾ", "ሆ"),
            # ዐ family merges into አ, then the 4th form into the 1st
            ("ዐ", "አ"),
            ("ዕ", "እ"),
            ("ዓ", "አ"),
            ("ኣ", "አ"),
            ("ሠ", "ሰ"),
            ("ሧ", "ሷ"),
            ("ፀ", "ጸ"),
            ("ፆ", "ጾ"),
            ("ሐበሻ", "ሀበሻ"),
            ("ዓለም", "አለም"),
            ("ሠላም", "ሰላም"),
            ("ፀሐይ", "ጸሀይ"),
        ]

    def test_normalize(self):
        for original, expected in self.test_cases:
            with self.subTest(original=original):
                self.assertEqual(self.normalize(original, "am"), expected)

    def test_letters_left_unchanged(self):
        for letter in "ኸኧሇቇኇጏፇኈኊኌኍሗጿቐቘዃ":
            with self.subTest(letter=letter):
                self.assertEqual(self.normalize(letter, "am"), letter)


class TestNormalizeTigrinya(unittest.TestCase):
    def setUp(self):
        self.normalize = TextNormalizer().normalize

        self.test_cases = [
            # ሐ and ኀ families merge into ሀ; 1st and 4th forms stay apart
            ("ሐ", "ሀ"),
            ("ሓ", "ሃ"),
            ("ኀ", "ሀ"),
            ("ኃ", "ሃ"),
            ("ኋ", "ሗ"),
            # the whole ኸ family joins ሀ, plus ዃ → ሗ
            ("ኸ", "ሀ"),
            ("ኻ", "ሃ"),
            ("ኽ", "ህ"),
            ("ዃ", "ሗ"),
            ("ዐ", "አ"),
            ("ዓ", "ኣ"),
            ("ኧ", "አ"),
            ("ሠ", "ሰ"),
            ("ፀ", "ጸ"),
            # ቐ merges into ቀ for its 7 vowel forms and ቛ
            ("ቐ", "ቀ"),
            ("ቕ", "ቅ"),
            ("ቛ", "ቋ"),
            ("ሓደ", "ሃደ"),
            ("ዓዲ", "ኣዲ"),
            ("ቐሺ", "ቀሺ"),
        ]

    def test_normalize(self):
        for original, expected in self.test_cases:
            with self.subTest(original=original):
                self.assertEqual(self.normalize(original, "ti"), expected)

    def test_letters_left_unchanged(self):
        for letter in "ሃኣሇቇኇጏፇኈኊኌኍቘቚቜቝዀዂዄዅ":
            with self.subTest(letter=letter):
                self.assertEqual(self.normalize(letter, "ti"), letter)


class TestNormalizeGeneral(unittest.TestCase):
    def setUp(self):
        self.normalize = TextNormalizer().normalize

    def test_normalizing_twice_changes_nothing(self):
        ethiopic = "".join(chr(c) for c in range(0x1200, 0x1380))
        for language in ["am", "ti"]:
            with self.subTest(language=language):
                once = self.normalize(ethiopic, language)
                self.assertEqual(self.normalize(once, language), once)

    def test_non_ethiopic_text_unchanged(self):
        self.assertEqual(self.normalize("Hello, 123!", "am"), "Hello, 123!")

    def test_unsupported_language_rejected(self):
        with self.assertRaises(ValueError):
            self.normalize("ሀ", "gez")


if __name__ == "__main__":
    unittest.main()
