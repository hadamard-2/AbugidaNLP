# AbugidaNLP
Natural Language Processing tools and resources for Ethiopian languages.

---

## Introduction
AbugidaNLP is an open-source library focused on developing NLP tools tailored to Ethiopian languages. The library aims to support tasks like calendar system conversion, numeral conversion, and transliteration between Ethiopic and Latin scripts. As one of the first steps towards bridging the gap in NLP tools for underrepresented languages, AbugidaNLP aspires to grow into a comprehensive toolkit for linguists, researchers, and developers.

---

## Key Features
AbugidaNLP is currently in its infancy, offering:
- **Transliteration**: Convert text between Ethiopic and Latin scripts.
- **Calendar System Conversion**: Seamlessly convert dates between Ethiopic and Gregorian calendars.
- **Numeral System Conversion**: Translate numbers between Ge'ez and Hindu-Arabic numeral systems.

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Installation
Install AbugidaNLP using pip:
```bash
pip install abugida
```

---

## Quick Start

Here’s how to get started with AbugidaNLP:

```python
from abugida import ScriptConverter  # Import the ScriptConverter class from AbugidaNLP

# Initialize the ScriptConverter
converter = ScriptConverter()

# Forward transliteration: Convert Ethiopic script to Latin script
result_fwd = converter.transliterate("በመተባበራችን", "fwd")
print(result_fwd)  # Output: bemetebaberacn

# Backward transliteration: Convert Latin script to Ethiopic script
result_bwd = converter.transliterate("merejawoc", "bwd")
print(result_bwd)  # Output: መረጃዎች
```

### Explanation:
1. **Import the library**: The `ScriptConverter` class handles script conversions.
2. **Initialize**: Create an instance of the `ScriptConverter` to use its methods.
3. **Transliteration**:
   - Use the `"fwd"` mode for Ethiopic to Latin conversion.
   - Use the `"bwd"` mode for Latin to Ethiopic conversion.

### Calendar Conversion

```python
from abugida import CalendarConverter

converter = CalendarConverter()

# Ethiopian Calendar (EC) to Gregorian Calendar (GC)
print(converter.convert("2017-04-29", "EC", "GC"))  # Output: 2025-01-07 (Genna)

# Gregorian Calendar (GC) to Ethiopian Calendar (EC)
print(converter.convert("2024-09-11", "GC", "EC"))  # Output: 2017-01-01 (Enkutatash)

# Pagume 6 exists only in leap years (years where year % 4 == 3)
print(converter.convert("2015-13-06", "EC", "GC"))  # Output: 2023-09-11
```

Dates are written as `"YYYY-MM-DD"`, with Pagume as month `13`. Conversion goes through the Julian Day Number using the Beyene-Kudlek algorithm, the same one used by ICU. Ethiopian dates use the Amete Mihret era, and Gregorian dates use the proleptic Gregorian calendar.

### Numeral Conversion

```python
from abugida import NumeralConverter

converter = NumeralConverter()

# Hindu-Arabic ("ha") to Ge'ez ("gz")
print(converter.convert(2017, "ha", "gz"))       # Output: ፳፻፲፯
print(converter.convert(100000000, "ha", "gz"))  # Output: ፼፼

# Ge'ez ("gz") to Hindu-Arabic ("ha")
print(converter.convert("፯፻፷፭፼፵፫፻፳፩", "gz", "ha"))  # Output: 7654321
```

Ge'ez numerals follow the CLDR `%ethiopic` rule set, so output matches ICU. When parsing, an explicit `፩` before `፻` or `፼` (as in `፩፻`) is accepted, and malformed numerals such as `፻፻` raise a `ValueError`.

---

## Documentation
Documentation for AbugidaNLP is under construction. Stay tuned for detailed usage examples and API references.

---

## Contributing
We welcome contributions to AbugidaNLP! Whether it's improving documentation, adding new features, or fixing bugs, your help is valuable.

### Steps to Contribute:
1. Fork the repository.
2. Create a new branch for your feature/bugfix.
3. Submit a pull request.

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments
Special thanks to the following resources for their inspiration and insights:
- [A Look at Ethiopic Numerals](https://www.geez.org/Numerals/)
- [The System for Ethiopic Representation in ASCII](https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=96a6d78a3fced66214611339a0f95441ab4dc992)
- [The Ethiopic Calendar](https://www.geez.org/Calendars/), for its summary of the Beyene-Kudlek algorithm (B. Beyene and M. Kudlek, "Calendars in Ethiopia", International Conference of Ethiopian Studies XV)
- [Unicode CLDR](https://github.com/unicode-org/cldr/blob/main/common/rbnf/root.xml), for the `%ethiopic` rule set that defines the numeral convention
- [ICU](https://icu.unicode.org/), whose Ethiopic calendar and numeral formatting were used to verify conversions

## Contact
For questions or support, please open an issue.

