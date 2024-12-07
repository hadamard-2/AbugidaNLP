import unittest
from convert_script import transliterate


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

    def test_transliterate_fwd(self):
        for ethiopic, latin in self.test_cases:
            with self.subTest(original=ethiopic, expected=latin):
                self.assertEqual(transliterate(ethiopic, "fwd"), latin)

    def test_transliterate_bwd(self):
        for ethiopic, latin in self.test_cases:
            with self.subTest(original=latin, expected=ethiopic):
                self.assertEqual(transliterate(latin, "bwd"), ethiopic)


if __name__ == "__main__":
    unittest.main()
