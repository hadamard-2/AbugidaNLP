# Number ↔ Words Implementation Plan

> **Status (history, 2026-11-25):** this plan has been carried out on branch `feat/number-words`, and several defaults have changed since; see the status note at the top of the design doc. Its word lists and test values are history, not current behaviour.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `NumberWordConverter` to AbugidaNLP: one default written form from a number (`to_words`), and a number from any accepted spoken variant (`to_number`), for Amharic, Tigrinya and Afaan Oromoo, in the modes cardinal, ordinal, ordinal_num, year and currency.

**Architecture:** Each language has its own composer module that builds words from an `int` and its own lexicon of accepted tokens for parsing. All word lists live in one data-only module, so the author can review spellings without reading logic. A shared parser core turns tokens into `(kind, value)` items and folds them with a scale-grouping grammar. Each language plugs in its token rules: Tigrinya "-ን", Oromo "fi"/"-ii" and Oromo head-first order. `NumberWordConverter` handles what all languages share: validating the language and mode, negatives, decimals, currency amounts, and the overflow ceiling. It delegates the rest to the language modules.

**Tech Stack:** Python ≥ 3.10, standard library only (`decimal`, `re`, `random` in tests), `unittest`.

**Spec:** `docs/superpowers/specs/2026-10-28-number-words-design.md`. Read it in full before starting any task. Its "Language rules" section is the source for every word and every default form. Gemini's background answers are in the same folder (`2026-10-28-number-words-gemini-*.md`); they are only to be consulted where the spec says "the forms in the Gemini file".

## Global Constraints

- Python ≥ 3.10, standard library only; `install_requires=[]` stays empty.
- **Do not read num2words or num2words2 source code or test files**, anywhere (they are LGPL-2.1; this library is MIT). Running the installed package as a black box (Task 8 only) is allowed.
- Tests are `unittest`, in `tests/`, files named `*_test.py`. Run all with `python3 -m unittest discover -s tests -p '*_test.py'`.
- Follow the existing module style (`abugida/normalize_text.py`, `abugida/convert_numeral.py`): one class, class-level tables, Google-style docstrings with Args/Returns/Raises.
- All word tables are in `abugida/number_words/tables.py`, data only.
- Ge'ez script for `am` and `ti`; Qubee (Latin) for `om`. No romanized Amharic or Tigrinya anywhere.
- Unsupported language or mode → `ValueError`. Unsupported currency code for a language → `ValueError`. Value ≥ the language's maxval → `OverflowError`. Ordinal of zero, a negative or a non-integer → `TypeError`.
- maxval (first value that overflows): `am` 10¹⁵, `ti` 10¹², `om` 10¹².
- Mode names: `cardinal` (default), `ordinal`, `ordinal_num`, `year`, `currency`.
- Markdown files: one line per paragraph, no hard wrapping.
- Commit messages: Conventional Commits (`feat:`, `test:`, `docs:`), no attribution lines. Never `git push`.
- Work on branch `feat/number-words`.

## Decisions this plan makes where the spec is silent

These are plan-level calls, and the author reviews them through the test tables. Each one is pinned by a test in the task that owns it.

1. **Components.** A number splits into components: one per non-zero scale group of 10³ and up (multiplier + scale word), then hundreds, then the sub-100 rest. A teen (11–19) is one component. Tens + units (21–99, units ≠ 0) are two components. The multiplier of a scale word ≥ 10³ is rendered as a standalone cardinal, and its own internal joining stays inside it.
2. **Tigrinya "-ን".** If a number has more than one component, every component gets "ን" appended to its last word. The one exception is ሚእቲ, which becomes ሚእትን. A component's multiplier is never suffixed, only the component's last word. Examples: 21,000 → "ዕስራን ሓደን ሺሕ"; 21,005 → "ዕስራን ሓደን ሺሕን ሓሙሽተን"; 1,500,000 → "ሚልዮንን ሓሙሽተ ሚእቲ ሺሕን".
3. **Oromo order and "fi".** Each scale component is written as scale word + multiplier ("kuma lama", "dhibba sadii"). "fi" goes only before the last component. Tens + units are one Oromo component ("digdamii shan"). A teen is one component. A multiplier that is itself compound keeps its own "fi": 125,000 → "kuma dhibba tokko fi digdamii shan".
4. **Ordinals of compounds.** am: the last word is swapped using the ordinal table. om: suffix on the last word. ti from 11 up: "መበል" + the cardinal unchanged (including its "-ን").
5. **Currency.** The amount is rounded to 2 places with `ROUND_HALF_UP`. Whole part 0 with cents > 0 → only the cents part ("ሃምሳ ሳንቲም"). Cents 0 → only the whole part. Joiners: am "ከ" between the parts; ti and om none. `to_number(..., to="currency")` with only a sub-unit returns the code whose sub-unit word matched first in the language's currency table order (ETB first).
6. **Decimals.** `float` goes through `Decimal(repr(x))`. A `Decimal` or numeric string whose value is integral is treated as an `int` ("2.0" → "ሁለት"). Fraction digits are read one by one with the digit words, and 0 is the language's zero word.
7. **Years.** Same as cardinal, including negatives.

## Review Focus

1. **Adjacent numbers that aren't one number.** "አምስት ስድስት", "ሃያ ሠላሳ", and "ሺህ ሺህ" are not single numbers. `to_number` must raise `ValueError` and must not add them up. → Task 3, `test_rejects_non_numbers`.
2. **Mixed digits and words.** "3 ሚሊዮን", "1.5 ሚሊዮን", "2 ሺህ 500". People type these into transcripts. Expected `int` results: 3000000, 1500000 and 2500. → Task 3, `test_mixed_digits_and_words`.
3. **Normalizer-equivalent spellings in the lexicon.** "ሀምሳ", "ኃምሳ" and "አሥራ" vs "አስራ" must all parse, which only works if lexicon keys are normalized exactly as the tokens are. → Task 3, `test_homophone_spellings`.
4. **Oromo dropped "tokko" before "dhibba".** "kuma dhibba lama soddomii afur" reads greedily as 234,000. That follows the spec's "default reading wins" rule, and a person might expect 1234. This plan pins 234000 and calls it out to the author. → Task 7, `test_dropped_tokko_reads_greedily`.
5. **Boundary values.** maxval − 1 must convert. maxval must raise `OverflowError` in both directions ("አንድ ሺህ ትሪሊዮን" in am). 0, and exactly a scale (10⁶ → "አንድ ሚሊዮን", ti "ሚልዮን"), must convert. → Tasks 1, 4 and 6, `test_bounds`.

---

## File Structure

- Create `abugida/number_words/__init__.py`: empty package marker.
- Create `abugida/number_words/tables.py`: every word list for all three languages (default forms, accepted variants, ordinal words, currency words). Data only.
- Create `abugida/number_words/parser.py`: the shared token-to-number grammar.
- Create `abugida/number_words/amharic.py`, `tigrinya.py`, `oromo.py`: per-language `cardinal(n) -> str`, `ordinal(n, gender) -> str`, `ordinal_num(n, gender) -> str`, a `lex(token) -> list[Item]` token reader, and language-specific parse hooks.
- Create `abugida/convert_number_words.py`: `NumberWordConverter`, the public class.
- Modify `abugida/__init__.py`: export `NumberWordConverter`.
- Create `tests/number_words_am_test.py`, `tests/number_words_ti_test.py`, `tests/number_words_om_test.py`, `tests/number_words_api_test.py`.
- Create `scripts/compare_num2words2.py` (dev-only).
- Modify `README.md`; create `docs/number_words.md`.

---

### Task 1: Package skeleton, Amharic tables and Amharic cardinals

**Files:**
- Create: `abugida/number_words/__init__.py`, `abugida/number_words/tables.py`, `abugida/number_words/amharic.py`, `abugida/convert_number_words.py`
- Modify: `abugida/__init__.py`
- Test: `tests/number_words_am_test.py`, `tests/number_words_api_test.py`

**Interfaces:**
- Produces:
  - `NumberWordConverter.to_words(value: int | float | Decimal | str, language: str, to: str = "cardinal", currency: str | None = None, gender: str = "m") -> str`
  - `amharic.cardinal(n: int) -> str` for 0 ≤ n < 10¹⁵
  - `amharic.MAXVAL = 10**15`
  - `tables.AM`: a dict with the keys `digits` (list of 11, index = value), `teens_prefix` ("አሥራ"), `tens` (dict 20..90 → word), `scales` (dict 100, 10³, 10⁶, 10⁹, 10¹² → word), `negative` ("ኔጌቲቭ"), `point` ("ነጥብ"), `ordinal_last` (dict word → ordinal word), `currencies` (dict code → (unit, subunit)), `currency_joiner` ("ከ"), and `accept` (dict variant word → default word).
  - A shared `components(n: int) -> list[tuple[int, int]]` in `abugida/number_words/__init__.py` that implements decision 1. It returns `(multiplier, scale)` for scale groups and hundreds, and `(value, 1)` for the rest, which is a teen, a tens value or a units value. For example, 2026 → `[(2, 1000), (20, 1), (6, 1)]` and 615 → `[(6, 100), (15, 1)]`.

- [ ] **Step 1: Write the failing tests.** In `tests/number_words_am_test.py`, add `TestAmharicCardinal` with a table test using `subTest`:

```python
CASES = [
    (0, "ዜሮ"), (1, "አንድ"), (10, "አሥር"), (11, "አሥራ አንድ"), (16, "አሥራ ስድስት"),
    (20, "ሃያ"), (21, "ሃያ አንድ"), (50, "ሃምሳ"), (60, "ስድሳ"), (99, "ዘጠና ዘጠኝ"),
    (100, "አንድ መቶ"), (101, "አንድ መቶ አንድ"), (125, "አንድ መቶ ሃያ አምስት"),
    (1000, "አንድ ሺህ"), (1500, "አንድ ሺህ አምስት መቶ"), (2015, "ሁለት ሺህ አሥራ አምስት"),
    (2026, "ሁለት ሺህ ሃያ ስድስት"), (10500, "አሥር ሺህ አምስት መቶ"),
    (10**6, "አንድ ሚሊዮን"), (21_000, "ሃያ አንድ ሺህ"), (125_000, "አንድ መቶ ሃያ አምስት ሺህ"),
]
```

Add `test_bounds`: `to_words(10**15 - 1, "am")` returns a string that starts with "ዘጠኝ መቶ ዘጠና ዘጠኝ ትሪሊዮን", and `to_words(10**15, "am")` raises `OverflowError`. In `tests/number_words_api_test.py`, add tests that `to_words(1, "xx")` and `to_words(1, "am", to="roman")` raise `ValueError`, and that `from abugida import NumberWordConverter` works.

- [ ] **Step 2: Run them and confirm they fail.** Run `python3 -m unittest tests.number_words_am_test tests.number_words_api_test -v`. Expected: `ImportError` / `ModuleNotFoundError`.

- [ ] **Step 3: Write `tables.AM`** with the exact words from the spec's Amharic section. `accept` holds ባዶ, አንዲት, አምሳ, ኃምሳ, ሀምሳ, ስልሳ, ሺ, ሲቀነስ and አሉታዊ, plus the ordinal variants መጀመሪያ (→ አንደኛ) and ሺኛ (→ ሺህኛ). `ordinal_last` covers every digit 1–10 (አንደኛ ሁለተኛ ሦስተኛ አራተኛ አምስተኛ ስድስተኛ ሰባተኛ ስምንተኛ ዘጠነኛ አሥረኛ), every tens word (ሃያኛ ሠላሳኛ አርባኛ ሃምሳኛ ስድሳኛ ሰባኛ ሰማንያኛ ዘጠናኛ) and every scale (መቶኛ ሺህኛ ሚሊዮንኛ ቢሊዮንኛ ትሪሊዮንኛ). `currencies` = `{"ETB": ("ብር", "ሳንቲም"), "USD": ("ዶላር", "ሳንቲም")}`.

- [ ] **Step 4: Implement `components` and `amharic.cardinal`.** Join the components with spaces. A multiplier is always rendered as a full cardinal, including "አንድ" (the explicit-one rule). A `(value, 1)` component is the digit, the "አሥራ" + digit teen, or the tens word.

- [ ] **Step 5: Implement `NumberWordConverter.__init__` and `to_words`** for `int` input and `to="cardinal"` only. Validate the language (`am`, `ti`, `om`) and the mode, and check maxval. The other modes come in Task 2. Until then they raise `NotImplementedError`. Export the class from `abugida/__init__.py` and add it to `__all__`.

- [ ] **Step 6: Run the tests and confirm they pass.** Run the command from Step 2. Expected: OK.

- [ ] **Step 7: Commit.**

```bash
git add abugida/number_words abugida/convert_number_words.py abugida/__init__.py tests/number_words_am_test.py tests/number_words_api_test.py
git commit -m "feat: add Amharic cardinal number-to-words"
```

### Task 2: Amharic ordinals, years, negatives, decimals and currency (to_words)

**Files:**
- Modify: `abugida/number_words/amharic.py`, `abugida/convert_number_words.py`
- Test: `tests/number_words_am_test.py`

**Interfaces:**
- Consumes: `amharic.cardinal`, `tables.AM`.
- Produces:
  - `amharic.ordinal(n: int, gender: str = "m") -> str` (gender is ignored).
  - `amharic.ordinal_num(n: int, gender: str = "m") -> str`.
  - A shared helper in `NumberWordConverter`, `_split_decimal(value) -> tuple[bool, int, str]`, which returns (negative, integer part, fraction digits as a string, `""` if none). Tasks 4 and 6 reuse it.
  - Each language module exposes `NEGATIVE`, `POINT`, `ZERO` and `currency(whole: int, cents: int, code: str) -> str`.

- [ ] **Step 1: Write the failing tests.**
  - `test_ordinals`: 1→"አንደኛ", 3→"ሦስተኛ", 10→"አሥረኛ", 11→"አሥራ አንደኛ", 20→"ሃያኛ", 21→"ሃያ አንደኛ", 100→"መቶኛ", 1000→"ሺህኛ", 10**6→"ሚሊዮንኛ", 101→"አንድ መቶ አንደኛ", 200→"ሁለት መቶኛ", 2015→"ሁለት ሺህ አሥራ አምስተኛ".
  - `test_ordinal_num`: 3→"3ኛ", 2015→"2015ኛ".
  - `test_ordinal_rejects`: 0, -1 and 2.5 raise `TypeError` for both `ordinal` and `ordinal_num`.
  - `test_year`: 2015→"ሁለት ሺህ አሥራ አምስት", -44→"ኔጌቲቭ አርባ አራት".
  - `test_negative_and_decimal`: -2.5→"ኔጌቲቭ ሁለት ነጥብ አምስት", `Decimal("3.05")`→"ሦስት ነጥብ ዜሮ አምስት", "2.0"→"ሁለት", -7→"ኔጌቲቭ ሰባት".
  - `test_currency`: (12.5, "ETB")→"አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም", (1, "USD")→"አንድ ዶላር", (0.5, "ETB")→"ሃምሳ ሳንቲም", (2.005, "ETB")→"ሁለት ብር ከ አንድ ሳንቲም". ("EUR" and currency=None) with `to="currency"` raise `ValueError`.
- [ ] **Step 2: Run them and confirm they fail.** Run `python3 -m unittest tests.number_words_am_test -v`. Expected: `NotImplementedError` failures.
- [ ] **Step 3: Implement the methods.** In `amharic.ordinal`, a value that is exactly one scale (100, 10³, 10⁶, 10⁹, 10¹²) returns the bare scale ordinal. Otherwise, take the cardinal and swap its last word through `ordinal_last`. In `to_words`, the negative word comes before the integer cardinal. If there are fraction digits, add the point word and then one digit word per digit.
- [ ] **Step 4: Run the tests and confirm they pass.** Expected: OK.
- [ ] **Step 5: Commit** with `feat: add Amharic ordinals, years, decimals and currency`.

### Task 3: Parser core and Amharic to_number

**Files:**
- Create: `abugida/number_words/parser.py`
- Modify: `abugida/number_words/amharic.py`, `abugida/convert_number_words.py`
- Test: `tests/number_words_am_test.py`

**Interfaces:**
- Consumes: `tables.AM`, `TextNormalizer.normalize(text, language)` from `abugida.normalize_text`.
- Produces:
  - `parser.Item = tuple[str, int]`, where the kind is one of `"num"` (a digit, teen or tens word, or a digit-string token), `"scale"` (100 and up), `"neg"`, `"point"`, `"skip"` (conjunctions), `"ord"` (an ordinal word; the value is its number), or `"unit"` / `"subunit"` (the value is an index into the currency table).
  - `parser.fold_multiplier_first(items: list[Item]) -> int`, which raises `ValueError` on invalid order. Tasks 5 and 7 reuse it (Oromo uses it for the reversed-order fallback).
  - Each language module defines `lex(token: str) -> list[Item]` and raises `ValueError` on an unknown token.
  - `NumberWordConverter.to_number(text: str, language: str, to: str = "cardinal") -> int | Decimal | tuple[Decimal, str]`.

`fold_multiplier_first` follows this grammar, the algorithm the spec states:

```
total = 0; group = 0; last_small = None   # last "num" value inside the current group
for kind, v in items:
  num:   if last_small is not None and not (last_small >= 10 and v < 10 and last_small % 10 == 0): raise
         group += v; last_small = v
  scale 100:   if group >= 100 or group == 0 and last_small is not None: raise
               group = (group or 1) * 100; last_small = None      # multiplier 1–99 allowed ("አሥራ አምስት መቶ")
  scale ≥1000: if scale >= the smallest scale already applied to total, or group >= 1000: raise
               total += (group or 1) * scale; group = 0; last_small = None
return total + group
```

Within a group, the sub-100 part must strictly decrease: a tens word may be followed by a unit, and nothing else. Digit-string tokens ("3", "1.5", "500") come in as `num` with their value. A non-integral digit token is allowed only directly before a scale ≥ 1000, and the product must be integral.

- [ ] **Step 1: Write the failing tests.**
  - `test_round_trip_cardinal`: for every n in `range(0, 10001)`, `to_number(to_words(n, "am"), "am") == n`. Add 300 values from `random.Random(0).randrange(10**15)`.
  - `test_round_trip_modes`: ordinal and ordinal_num for 1..2000; year for 1..3000; currency for every whole amount in 0..300 combined with cents in (0, 1, 50, 99), excluding 0.00.
  - `test_accepts`: "ሺ አምስት መቶ"→1500, "መቶ"→100, "ሺህ"→1000, "ሚሊዮን"→10**6, "ሃያ አምስት"→25, "አምሳ"→50, "ስልሳ"→60, "ባዶ"→0, "አንዲት"→1, "ሲቀነስ አምስት"→-5, "አሉታዊ አምስት"→-5, "  አንድ መቶ  "→100. With `to="ordinal"`: "መጀመሪያ"→1, "ሺኛ"→1000, "መቶ አንደኛ"→101.
  - `test_mixed_digits_and_words`: "3 ሚሊዮን"→3000000, "1.5 ሚሊዮን"→1500000, "2 ሺህ 500"→2500.
  - `test_homophone_spellings`: "አስራ ስድስት"→16, "ኃምሳ"→50, "ሀምሳ"→50, "ሠላሳ" and "ሰላሳ"→30.
  - `test_rejects_non_numbers`: "አምስት ስድስት", "ሃያ ሠላሳ", "ሺህ ሺህ", "መቶ ሺህ መቶ ሺህ", "ቤት", "" → `ValueError`.
  - `test_decimal_and_currency_parse`: "ኔጌቲቭ ሁለት ነጥብ አምስት"→`Decimal("-2.5")`. With `to="currency"`: "አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም"→`(Decimal("12.50"), "ETB")`, "ሃምሳ ሳንቲም"→`(Decimal("0.50"), "ETB")`, "አንድ ዶላር"→`(Decimal("1.00"), "USD")`.
  - `test_overflow_parse`: "አንድ ሺህ ትሪሊዮን" → `OverflowError`.
  - `test_ordinal_num_parse`: "3ኛ"→3 with `to="ordinal_num"`.
- [ ] **Step 2: Run them and confirm they fail.** Expected: `to_number` is not defined.
- [ ] **Step 3: Write `parser.fold_multiplier_first`, `amharic.lex` and `to_number`.** Build `amharic.lex`'s lookup dict once, from `tables.AM` (defaults, accepts, ordinal words and currency words). Pass every key through `TextNormalizer().normalize(key, "am")`, and do the same to each token before looking it up. `to_number` does the following:
  1. Strip the text and split it on whitespace.
  2. Lex each token.
  3. Handle a leading `neg`.
  4. Split at `point`. The fraction digits must each be a single digit 0–9.
  5. For `ordinal`, the last item must be `ord`. Fold its value as a `num`, or as a `scale` if it is ≥ 100.
  6. For `currency`, split at the unit, the "ከ" joiner and the sub-unit.
  7. Fold the result and check maxval.
- [ ] **Step 4: Run the tests and confirm they pass.** Run `python3 -m unittest tests.number_words_am_test -v`. Expected: OK.
- [ ] **Step 5: Commit** with `feat: add Amharic words-to-number parsing`.

### Task 4: Tigrinya to_words, all modes

**Files:**
- Modify: `abugida/number_words/tables.py` (add `TI`)
- Create: `abugida/number_words/tigrinya.py`
- Modify: `abugida/convert_number_words.py` (register `ti`)
- Test: `tests/number_words_ti_test.py`

**Interfaces:**
- Consumes: `components`, `_split_decimal`, and the language module contract from Tasks 1–2.
- Produces: `tigrinya.cardinal`, `ordinal`, `ordinal_num` (all with a `gender` keyword), `MAXVAL = 10**12`, and `tables.TI`, shaped like `tables.AM` plus `ordinals_1_10` (dict n → (masculine, feminine)), `ordinal_prefix` ("መበል") and `conjunction` ("ን").

- [ ] **Step 1: Write the failing tests.** Every expected string comes from the spec's Tigrinya section or from decision 2:

```python
CASES = [
    (0, "ባዶ"), (5, "ሓሙሽተ"), (6, "ሽዱሽተ"), (12, "ዓሰርተ ክልተ"), (20, "ዕስራ"),
    (21, "ዕስራን ሓደን"), (35, "ሰላሳን ሓሙሽተን"), (99, "ተስዓን ትሽዓተን"),
    (100, "ሚእቲ"), (101, "ሚእትን ሓደን"), (125, "ሚእትን ዕስራን ሓሙሽተን"), (200, "ክልተ ሚእቲ"),
    (615, "ሽዱሽተ ሚእትን ዓሰርተ ሓሙሽተን"), (812, "ሸሞንተ ሚእትን ዓሰርተ ክልተን"),
    (1000, "ሺሕ"), (1500, "ሺሕን ሓሙሽተ ሚእትን"), (2015, "ክልተ ሺሕን ዓሰርተ ሓሙሽተን"),
    (2025, "ክልተ ሺሕን ዕስራን ሓሙሽተን"), (2026, "ክልተ ሺሕን ዕስራን ሽዱሽተን"), (5000, "ሓሙሽተ ሺሕ"),
    (21_000, "ዕስራን ሓደን ሺሕ"), (21_005, "ዕስራን ሓደን ሺሕን ሓሙሽተን"),
    (10**6, "ሚልዮን"), (1_500_000, "ሚልዮንን ሓሙሽተ ሚእቲ ሺሕን"), (10**9, "ቢልዮን"),
]
```

  - `test_ordinals`: 1→"ቀዳማይ", 3→"ሳልሳይ", 10→"ዓስራይ", 3 with `gender="f"`→"ሳልሰይቲ", 11→"መበል ዓሰርተ ሓደ", 21→"መበል ዕስራን ሓደን", 100→"መበል ሚእቲ".
  - `test_ordinal_num`: 1→"1ይ", 10→"10ይ", 3 with `gender="f"`→"3ይቲ", 11→"መበል 11", 100→"መበል 100".
  - `test_negative_decimal`: -2.5→"ኣሉታ ክልተ ነጥቢ ሓሙሽተ", 0.05→"ባዶ ነጥቢ ባዶ ሓሙሽተ".
  - `test_currency`: (12.5, "ETB")→"ዓሰርተ ክልተ ብር ሓምሳ ሳንቲም", (21.25, "ETB")→"ዕስራን ሓደን ብር ዕስራን ሓሙሽተን ሳንቲም", (3, "ERN")→"ሰለስተ ናቕፋ", (1.5, "USD")→"ሓደ ዶላር ሓምሳ ሳንቲም", (2, "EUR")→"ክልተ ዩሮ". "GBP" raises `ValueError`.
  - `test_bounds`: 10**12 - 1 converts; 10**12 raises `OverflowError`.
  - `test_gender_on_cardinal_ignored`: `to_words(1, "ti", gender="f")` → "ሓደ". Feminine applies only to ordinals.
- [ ] **Step 2: Run them and confirm they fail.** Run `python3 -m unittest tests.number_words_ti_test -v`.
- [ ] **Step 3: Write `tables.TI` and `tigrinya.py`.** Implement decision 2 for joining. A teen is one component, and its "ን" goes on the unit word. A multiplier is rendered with `cardinal` and never takes "ሓደ"; a scale group whose multiplier is 1 is the bare scale word. `accept` holds every Tigrinya "Accept" item from the spec: ዜሮ, ሓንቲ, ሽድሽተ, ሸድሽተ, ሾብዓተ, ሾሞንተ, ተሽዓተ, ትሻዓተ, እስራ, ሱሳ, ቴስዓ, ሽሕ, ሺ, ሚሊዮን, ቢሊዮን, ኣሉታዊ, ሚነስ, ኔጌቲቭ, ሰንት, and the "አ"-initial spellings of ኣርባዕተ, ኣርብዓ and ኣሉታ.
- [ ] **Step 4: Run the tests and confirm they pass.**
- [ ] **Step 5: Commit** with `feat: add Tigrinya number-to-words`.

### Task 5: Tigrinya to_number

**Files:**
- Modify: `abugida/number_words/tigrinya.py`
- Test: `tests/number_words_ti_test.py`

**Interfaces:**
- Consumes: `parser.fold_multiplier_first`, `parser.Item`, and `to_number` from Task 3.
- Produces: `tigrinya.lex(token) -> list[Item]`.

`tigrinya.lex` does the following:
- The token "ን" on its own is `skip`.
- A token that ends in "ን" and isn't in the lexicon has the "ን" stripped and is looked up again. "ሚእትን" maps to ሚእቲ, and "ሚእት" on its own does as well.
- "ምስ", "ጥራይ" and "ጥራሕ" are `skip`, in `currency` mode only.
- "መበል" is a prefix marker. `to_number` with `to="ordinal"` requires either "መበል" plus a cardinal or a dedicated word, and accepts "መበል" plus a dedicated word.
- `ordinal_num` accepts "3ይ", "3ይቲ", "3-ይ" and "መበል 11".

- [ ] **Step 1: Write the failing tests.**
  - `test_round_trip`: the same ranges and modes as Task 3. Round-trip ordinals and ordinal_num with both genders.
  - `test_accepts_conjunction_patterns`: all of these → 1500: "ሺሕን ሓሙሽተ ሚእትን", "ሓደ ሺሕን ሓሙሽተ ሚእትን", "ሽሕን ሓሙሽተ ሚእቲ", "ሽሕ ሓሙሽተ ሚእቲ", "ሽሕ ን ሓሙሽተ ሚእቲ", "ዓሰርተ ሓሙሽተ ሚእቲ", "ሺ ሓሙሽተ ሚእቲ". And → 25: "ዕስራን ሓሙሽተን", "ዕስራን ሓሙሽተ", "ዕስራ ሓሙሽተን", "ዕስራ ሓሙሽተ", "ዕስራ ን ሓሙሽተ".
  - `test_accepts_words`: "ዜሮ"→0, "ሓንቲ"→1, "ሽድሽተ"→6, "ሾብዓተ"→7, "ሱሳ"→60, "ቴስዓ"→90, "እስራ"→20, "አርባዕተ"→4, "ሓደ ሚልዮን"→10**6, "ሚሊዮን"→10**6, "ሚነስ ሓሙሽተ"→-5, "ኣሉታዊ ሓሙሽተ"→-5.
  - `test_ordinal_accepts`: "መበል ሓደ"→1, "መበል ቀዳማይ"→1, "ቀዳመይቲ"→1, "3-ይ"→3 (ordinal_num).
  - `test_currency_accepts`: "ዓሰርተ ክልተ ብርን ሓምሳ ሳንቲምን", "ዓሰርተ ክልተ ብር ምስ ሓምሳ ሰንት" and "ዓሰርተ ክልተ ብር ሓምሳ ሳንቲም ጥራይ" → `(Decimal("12.50"), "ETB")`; "ሰለስተ ናቕፋ"→`(Decimal("3.00"), "ERN")`.
  - `test_rejects_non_numbers`: "ሓሙሽተ ሽዱሽተ", "ዕስራ ሰላሳ", "ዓሰርተን ሓሙሽተን ሓሙሽተ" → `ValueError`.
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement `tigrinya.lex`** and the Tigrinya branches in `to_number`. Normalize lexicon keys and tokens with `TextNormalizer().normalize(…, "ti")`. Strip "ን" before normalizing.
- [ ] **Step 4: Run all tests and confirm they pass.** Run `python3 -m unittest discover -s tests -p '*_test.py'`.
- [ ] **Step 5: Commit** with `feat: add Tigrinya words-to-number parsing`.

### Task 6: Afaan Oromoo to_words, all modes

**Files:**
- Modify: `abugida/number_words/tables.py` (add `OM`)
- Create: `abugida/number_words/oromo.py`
- Modify: `abugida/convert_number_words.py` (register `om`)
- Test: `tests/number_words_om_test.py`

**Interfaces:**
- Consumes: `components`, `_split_decimal`, the language module contract.
- Produces: `oromo.cardinal`, `ordinal`, `ordinal_num`, `MAXVAL = 10**12`, and `tables.OM`, shaped like the others plus `tens_linked` (dict 20..90 → the "-ii" form), `ordinal_irregular` (dict word → ordinal) and `conjunction` ("fi").

- [ ] **Step 1: Write the failing tests.**

```python
CASES = [
    (0, "zeeroo"), (6, "ja'a"), (11, "kudha tokko"), (19, "kudha sagal"), (20, "digdama"),
    (21, "digdamii tokko"), (99, "sagaltamii sagal"), (100, "dhibba tokko"), (200, "dhibba lama"),
    (101, "dhibba tokko fi tokko"), (125, "dhibba tokko fi digdamii shan"), (1000, "kuma tokko"),
    (1500, "kuma tokko fi dhibba shan"), (2015, "kuma lama fi kudha shan"),
    (2026, "kuma lama fi digdamii ja'a"), (5000, "kuma shan"),
    (5327, "kuma shan dhibba sadii fi digdamii torba"), (10**6, "miiliyoona tokko"),
    (125_000, "kuma dhibba tokko fi digdamii shan"),
    (1125, "kuma tokko dhibba tokko fi digdamii shan"),
]
```

  - `test_ordinals`: 1→"tokkoffaa", 2→"lamaffaa", 3→"sadaffaa", 4→"arfaffaa", 5→"shanaffaa", 10→"kurnaffaa", 100→"dhibbaffaa", 21→"digdamii tokkoffaa", 15→"kudha shanaffaa".
  - `test_ordinal_num`: 3→"3ffaa".
  - `test_negative_decimal`: -2.5→"negaatiivii lama tuqaa shan".
  - `test_currency`: (12.5, "ETB")→"kudha lama qarshii shantama saantima", (1, "USD")→"tokko doolaara", (0.5, "USD")→"shantama seentii", (2, "EUR")→"lama yuuroo". "ERN" raises `ValueError`.
  - `test_bounds`: 10**12 - 1 converts; 10**12 raises `OverflowError`.
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Write `tables.OM` and `oromo.py`.** Implement decision 3. Ordinals: if the last word is in `ordinal_irregular`, use that entry (tokko, lama, sadii, afur, kudhan, plus the variants listed in the spec). Otherwise add "ffaa" after a vowel, or "affaa" after a consonant. The `ordinal_irregular` table is data, kept in `tables.OM`.
- [ ] **Step 4: Run the tests and confirm they pass.**
- [ ] **Step 5: Commit** with `feat: add Afaan Oromoo number-to-words`.

### Task 7: Afaan Oromoo to_number

**Files:**
- Modify: `abugida/number_words/oromo.py`, `abugida/number_words/parser.py`
- Test: `tests/number_words_om_test.py`

**Interfaces:**
- Consumes: `parser.Item`, `parser.fold_multiplier_first` (used for the reversed-order fallback).
- Produces: `oromo.lex(token) -> list[Item]` and `parser.fold_head_first(items: list[Item]) -> int` (raises `ValueError`).

`fold_head_first` reads head-first numbers. A scale word ≥ 1000 takes as its multiplier the longest valid head-first sub-1000 phrase that follows it. If no number follows, or the next item is a larger scale, the multiplier is 1. "dhibba" takes one number 1–9 after it, and 1 if none follows. Scales must strictly decrease. `to_number` tries `fold_head_first` first and falls back to `fold_multiplier_first` only if that raises (the "default reading wins" rule).

`oromo.lex` lowercases the token and strips a trailing comma. It also handles:
- "fi" → `skip`.
- A trailing doubled vowel, for lengthened forms ("tokkoo", "lamaa"): retry with one vowel dropped.
- "kudha-tokko" and "kudhatokko": split off "kudha".
- `"bara"` → `skip`, in `year` mode only.
- Year mode: when the items are two sub-100 numbers, the first being 10–99 with no scale anywhere, the result is first × 100 + second.

- [ ] **Step 1: Write the failing tests.**
  - `test_round_trip`: the same ranges and modes as Task 3.
  - `test_accepts`: "kuma fi dhibba shan", "kuma dhibba shan", "kuma tokkoo fi dhibba shan", "kuma tokko, dhibba shan" → 1500; "digdama tokko", "digdama fi tokko", "digdamii tokko" → 21; "kudhatokko", "kudha-tokko", "kudhan fi tokko" → 11; "jaha", "jaa" → 6; "duwwaa" → 0; "miliyoona" → 10**6; "hir'uu shan", "minus shan" → -5; "lama tuqaa shan" → `Decimal("2.5")`; "lama qabxii shan" → `Decimal("2.5")`.
  - `test_reversed_order_fallback`: "lama kuma" → 2000, "shan dhibba" → 500, "kuma lama dhibba shan" → 2500 (head-first wins).
  - `test_dropped_tokko_reads_greedily`: "kuma dhibba lama soddomii afur" → 234000.
  - `test_year_two_part`: `to_number("digdamii kudha shan", "om", to="year")` → 2015, and "bara kuma lama fi kudha shan" → 2015 in year mode. `to_number("digdamii kudha shan", "om")` → `ValueError`.
  - `test_ordinal_accepts`: "lammaffaa"→2, "afraffaa"→4, "kudhaffaa"→10 (ordinal); "3ffaa"→3 (ordinal_num).
  - `test_currency_accepts`: "qarshii shantama"→`(Decimal("50.00"), "ETB")`, "kudha lama birrii shantama saantima"→`(Decimal("12.50"), "ETB")`.
  - `test_rejects_non_numbers`: "shan ja'a", "digdama soddoma", "manna" → `ValueError`.
- [ ] **Step 2: Run them and confirm they fail.**
- [ ] **Step 3: Implement `parser.fold_head_first`, `oromo.lex` and the Oromo branches in `to_number`.**
- [ ] **Step 4: Run the whole suite and confirm it passes.** Run `python3 -m unittest discover -s tests -p '*_test.py'`. Expected: OK, including the 21 existing tests.
- [ ] **Step 5: Commit** with `feat: add Afaan Oromoo words-to-number parsing`.

### Task 8: Documentation and the num2words2 comparison script

**Files:**
- Create: `docs/number_words.md`, `scripts/compare_num2words2.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: the public API and `tables.AM`, `tables.TI` and `tables.OM`.

- [ ] **Step 1: Write `docs/number_words.md`.** For each language, add a table of default words (digits, teens, tens, scales, negative, point, currencies, ordinal words) and a second table of accepted variants. Generate both from `tables.py` with a one-off snippet so they match exactly, then commit the Markdown. Do not wrap lines.
- [ ] **Step 2: Add a "Number Words" section to `README.md`,** after "Numeral Conversion" and in the same style. Show the API examples from the spec, list `to=` modes and errors, link `docs/number_words.md`, and add the feature to the feature list near the top.
- [ ] **Step 3: Write `scripts/compare_num2words2.py`.** It is a CLI with `--lang {am,ti,om}`, `--to MODE`, `--start` and `--stop`. It imports `num2words2.num2words` and exits with a clear message if the package isn't installed. For each value it prints `value | ours | theirs` wherever they differ, then a count. Its docstring says to install num2words2 from its GitHub source and to set `CARGO_TARGET_DIR` to a disk with several GB free. It also lists the expected differences from the spec's Verification section. It is not imported by tests.
- [ ] **Step 4: Check the script.** Without num2words2 installed, `python3 scripts/compare_num2words2.py --lang am --start 0 --stop 50` prints the install message and exits non-zero. If `~/.cache/abugida-n2w2-build/env/bin/python` exists, run the script with it from the repo root for each language over 0–2100, and paste the summary counts into the task report for the author.
- [ ] **Step 5: Run the whole suite one last time.** Run `python3 -m unittest discover -s tests -p '*_test.py'`. Expected: OK.
- [ ] **Step 6: Commit** with `docs: document number-word conversion and add num2words2 comparison script`.
