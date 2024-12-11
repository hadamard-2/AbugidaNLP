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
- Python 3.8 or higher
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

## Contact
For questions or support, please open an issue.

