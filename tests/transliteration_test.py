import unittest
from convert_script import transliterate, transcribe


class TestTransliteration(unittest.TestCase):
    def setUp(self):
        self.test_cases = [
            ("ኢትዮጵያ", "ityoPya"),
            ("ሰባበረው", "sebaberew"),
            ("ልጆቻችን", "ljocacn"),
            ("ውሃ", "wha"),
            ("አገልግሎት", "egelglot"),
            ("መረጃዎች", "merejawoc"),
            ("ቁርጥራጭ", "qurTraC"),
            ("ማህበረሰብ", "mahbereseb"),
            ("ትርዒት", "tr'it"),
            ("ትዕይንት", "t'Iynt"),
        ]

    def test_transliterate(self):
        for original, expected in self.test_cases:
            with self.subTest(original=original, expected=expected):
                self.assertEqual(transliterate(original), expected)

    def test_transcribe(self):
        for expected, original in self.test_cases:
            with self.subTest(original=original, expected=expected):
                self.assertEqual(transcribe(original), expected)


if __name__ == "__main__":
    unittest.main()
