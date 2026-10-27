import json
import os
import tempfile
import unittest
from abugida import ScriptConverter


class TestTransliteration(unittest.TestCase):
    def setUp(self):
        self.transliterate = ScriptConverter().transliterate

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
                self.assertEqual(self.transliterate(ethiopic, "fwd"), latin)

    def test_transliterate_bwd(self):
        for ethiopic, latin in self.test_cases:
            with self.subTest(original=latin, expected=ethiopic):
                self.assertEqual(self.transliterate(latin, "bwd"), ethiopic)


class TestMappingTable(unittest.TestCase):
    def test_every_bundled_letter_round_trips(self):
        converter = ScriptConverter()
        for fidel in converter.ethiopic_latin_map:
            with self.subTest(fidel=fidel):
                latin = converter.transliterate(fidel, "fwd")
                self.assertEqual(converter.transliterate(latin, "bwd"), fidel)

    def test_open_o_letters_are_unsupported(self):
        # SERA defines no codes for the open-o letters
        converter = ScriptConverter()
        for fidel in ["ሇ", "ቇ", "ኇ", "ጏ", "ፇ"]:
            with self.subTest(fidel=fidel):
                with self.assertRaises(ValueError):
                    converter.transliterate(fidel, "fwd")

    def test_duplicate_codes_rejected_at_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            mapping_file = os.path.join(tmp_dir, "table.json")
            with open(mapping_file, "w", encoding="utf-8") as file:
                json.dump({"ቇ": "qWa", "ቋ": "qWa", "ለ": "le"}, file)

            with self.assertRaises(ValueError) as context:
                ScriptConverter(mapping_file)

        self.assertIn("qWa", str(context.exception))


if __name__ == "__main__":
    unittest.main()
