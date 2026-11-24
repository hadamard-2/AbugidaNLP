# Number ↔ words for Amharic, Tigrinya and Afaan Oromoo

> **Status (history, 2026-11-25):** this document records the design as approved on 2026-10-28. Several defaults have changed since, so treat the word lists and examples below as history, not as current behaviour. `docs/number_words.md` and the README are the current reference. Changes since approval:
> - Amharic: 60 is ስልሳ (ስድሳ accepted); every ordinal is its cardinal plus "-ኛ", so 1000th is "አንድ ሺህኛ"; negative words accepted are አሉታዊ, አሉታ and ማይነስ (ሲቀነስ dropped).
> - Tigrinya: "ሓደ" is written before a scale word ("ሓደ ሽሕ"); 1000 is ሽሕ; 6th–9th are ሻድሻይ, ሻብዓይ, ሻምናይ, ታሽዓይ; negative words accepted are ኣሉታዊ, ኔጌቲቭ, ነገቲቭ and ማይነስ (ሚነስ and አሉታ dropped).
> - `to_words(..., explicit_one=False)` leaves out the leading "one" for Amharic and Tigrinya numbers from 100 to 199.
> - Afaan Oromoo: a compound multiplier repeats its scale word ("kuma dhibba tokko fi kuma digdamii shan" is 125000); the parser also reads "fi" attached as "-f"/"-fi" and ordinals written as the plain word plus "ffaa".
> - Numeric ordinals (`ordinal_num`) have no upper limit.

## Intent

Add number-to-words and words-to-number conversion to AbugidaNLP for Amharic (`am`), Tigrinya (`ti`) and Afaan Oromoo (`om`). The driving use is normalizing an ASR dataset:

- **Training data:** transcripts that contain digits ("በ2015 ዓ.ም 3 ሚሊዮን ብር") get the digits spelled out so the text matches what was spoken.
- **Scoring:** number phrases in both the reference and the model output are turned back into digits before WER, so a valid spoken variant ("ሺ" vs "አንድ ሺህ") is not counted as an error.

Version 1 delivers the core conversion of a single number or number phrase in each direction. Finding and converting numbers inside running text is the next step (see Roadmap) and builds on this.

The feature replaces reliance on num2words2 for these languages. num2words2 has to stay output-compatible with upstream num2words and so keeps known errors (Amharic 16 spelled "አስራ" while every other teen uses "አሥራ"; "መቶ" alone vs "አንድ መቶ" inside larger numbers; Amharic negative word "ሰልቢ", which is Tigrinya; Oromo with the multiplier before the scale word, "shan dhibba"). This library has no such constraint. Throughout this document, "num2words2" means the current GitHub code (1.0.21, commit a7bde8c), not the older PyPI release 1.0.20, which still gives romanized Tigrinya.

## Goals

1. **Number → words, one default form.** Each input produces exactly one written form. The person preparing a dataset reviews each conversion and edits it when the speaker said a different variant; the library does not enumerate variants.
2. **Words → number, every variant.** The parser accepts every spoken variant the rules below describe (optional leading "one", spelling variants, conjunction patterns, word-order calques) without ever building a list of variants.
3. **Feature parity with num2words2** for these three languages: cardinals (including negatives and decimals), ordinals, numeric ordinals ("3ኛ"), years, and currency, in both directions.
4. **Round trip.** For every supported mode, parsing the default form returns the original value.

## Non-goals (v1)

- Converting numbers inside running text, in either direction. On the Roadmap.
- Choosing which spoken variant matches a recording. That is the dataset reviewer's job.
- Producing a list of variants from number-to-words.
- Phone numbers, times, Ge'ez numerals (፩፪፫) inside text. On the Roadmap. Converting Ge'ez numerals on their own stays with the existing `NumeralConverter`.
- Cheque wording (num2words2 does not support it for Amharic either).
- Languages beyond `am`, `ti`, `om`.

## Anti-goals

- **Copying num2words or num2words2 code or tests.** Both are LGPL-2.1 and AbugidaNLP is MIT. The implementation is written from this document. The builder must not read the num2words/num2words2 source or test files. Running the installed `num2words2` package as a black box to compare outputs is allowed, and is encouraged (see Verification).
- Re-introducing the upstream errors listed under Intent.
- Adding runtime dependencies. The library has `install_requires=[]` and stays that way.
- Romanized output for Tigrinya or Amharic. Both are written in Ge'ez script.
- Treating num2words2 output as the reference. Where it differs from this document, this document wins.

## Constraints

- Python ≥ 3.10, standard library only, `unittest` tests in `tests/` (named like `tests/number_words_test.py`), matching the existing modules (`NumeralConverter`, `TextNormalizer`): one class, per-language data held as class-level tables, docstrings in the existing style.
- Word tables are data, kept separate from the composition logic so the author can review and edit spellings without reading code.
- Arbitrary-size `int` input up to the largest scale word defined for the language. Above that, raise `OverflowError`. Do not fall back to printing digits.
- Unsupported language, mode or currency code raises `ValueError` (or `NotImplementedError` for a mode a language lacks). Never fall back silently to another currency.

## Public API (my call, adjustable)

A new class `NumberWordConverter` exported from `abugida/__init__.py`:

```python
converter = NumberWordConverter()

converter.to_words(1500, "am")                          # "አንድ ሺህ አምስት መቶ"
converter.to_words(3, "am", to="ordinal")               # "ሦስተኛ"
converter.to_words(3, "am", to="ordinal_num")           # "3ኛ"
converter.to_words(2015, "am", to="year")               # "ሁለት ሺህ አሥራ አምስት"
converter.to_words(12.5, "am", to="currency", currency="ETB")  # "አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም"
converter.to_words(-2.5, "am")                          # "ኔጌቲቭ ሁለት ነጥብ አምስት"

converter.to_number("ሺ አምስት መቶ", "am")                 # 1500
converter.to_number("ሦስተኛ", "am", to="ordinal")         # 3
converter.to_number("አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም", "am", to="currency")  # (Decimal("12.50"), "ETB")
```

- `to` is one of `cardinal` (default), `ordinal`, `ordinal_num`, `year`, `currency`, the same names as num2words2, and takes the same values in both methods.
- `to_words` accepts `int`, `float`, `decimal.Decimal`, or a numeric string. Decimals are read digit by digit after the point word ("ሁለት ነጥብ አምስት").
- `to_number` takes a string that is entirely one number phrase (surrounding whitespace allowed) and raises `ValueError` otherwise. It returns `int`, or `Decimal` when the phrase has a point word. With `to="currency"` it returns `(Decimal amount, currency code)`. Gender is not returned.
- Ordinal options such as gender go through keyword arguments (`gender="f"` for Tigrinya).

## Parsing approach (decided)

Words-to-number tokenizes on whitespace, runs each token through `TextNormalizer.normalize` for that language plus a per-language token-variant table, and checks that the tokens form a valid number using the usual scale-grouping rule: within a group, values must strictly decrease, and a scale word must be larger than anything seen since the last larger scale. Conjunction particles (Tigrinya "-ን", Oromo "fi" and vowel lengthening) are stripped or skipped before grouping. The grammar is what accepts the variants; there is no list of every variant. Afaan Oromoo is written in Latin script, so `TextNormalizer` does not apply to it: the token is lowercased and the Oromo variant table applied instead.

Structure the scanner so that it can later find the longest valid run of tokens inside a sentence. The Roadmap's running-text step reuses it.

## Language rules

The author supplied a researched rule set for each language on 2026-10-28. It is the primary source below and overrides the earlier Gemini answers, which are kept next to this document as background. Defaults are what the generator emits. "Accept" lists extra forms the parser must take. Items marked *(my call)* are choices the author has not confirmed. **The author reviews every language's test tables before they are final.**

### Amharic (`am`)

- **Digits:** ዜሮ, አንድ, ሁለት, ሦስት, አራት, አምስት, ስድስት, ሰባት, ስምንት, ዘጠኝ, አሥር. **Accept:** ባዶ (0), አንዲት (feminine 1).
- **Teens:** "አሥራ" + digit, no conjunction: አሥራ አንድ … አሥራ ዘጠኝ. 16 is "አሥራ ስድስት".
- **Tens:** ሃያ, ሠላሳ, አርባ, ሃምሳ (author), ስድሳ, ሰባ, ሰማንያ, ዘጠና. **Accept:** አምሳ/ኃምሳ/ሀምሳ for 50, ስልሳ for 60.
- **Compounds:** words placed side by side from the largest scale down, with no conjunction: "ሃያ አንድ", "ሁለት ሺህ ሃያ ስድስት", "አሥር ሺህ አምስት መቶ".
- **Default form (author):** always an explicit "one" before a scale word: 100 → "አንድ መቶ", 101 → "አንድ መቶ አንድ", 1500 → "አንድ ሺህ አምስት መቶ", 10⁶ → "አንድ ሚሊዮን". **Accept:** the scale word without "አንድ".
- **Scales:** መቶ, ሺህ, ሚሊዮን, ቢሊዮን, ትሪሊዮን *(my call to include 10¹²)* ⇒ maxval 10¹⁵. **Accept:** ሺ.
- **Accept also:** ሥ/ስ and the other homophone letters (via `TextNormalizer`); digits mixed with scale words ("3 ሚሊዮን").
- **Years (author):** read as ordinary cardinals: 2015 → "ሁለት ሺህ አሥራ አምስት".
- **Ordinals:** "-ኛ" on the last word of the cardinal: አንደኛ, ሁለተኛ, ሦስተኛ, አራተኛ, አምስተኛ, አሥረኛ, ሃያኛ. An ordinal that is a single scale word drops "አንድ", because "አንድ መቶኛ" means 1/100: 100th → "መቶኛ", 1000th → "ሺህኛ", 10⁶th → "ሚሊዮንኛ" (author, from Gemini). Everywhere else the explicit-one rule holds: 101st → "አንድ መቶ አንደኛ". **Accept:** መጀመሪያ for 1st, "ሺኛ", and "መቶ አንደኛ". Numeric: digits + "ኛ" ("3ኛ"). Zero and negatives raise `TypeError`.
- **Negative word (author):** ኔጌቲቭ. **Accept:** ሲቀነስ, አሉታዊ.
- **Point word:** ነጥብ.
- **Currency:** ETB (ብር / ሳንቲም), USD (ዶላር / ሳንቲም), joined with "ከ": "አሥራ ሁለት ብር ከ ሃምሳ ሳንቲም". Other codes raise.

### Tigrinya (`ti`), Ge'ez script

- **Digits:** ባዶ, ሓደ, ክልተ, ሰለስተ, ኣርባዕተ, ሓሙሽተ, ሽዱሽተ, ሸውዓተ, ሸሞንተ, ትሽዓተ, ዓሰርተ. **Accept:** ዜሮ (0), ሓንቲ (feminine 1), አ for ኣ at the start of words, ሽድሽተ/ሸድሽተ, ሾብዓተ, ሾሞንተ, ተሽዓተ/ትሻዓተ.
- **Teens:** "ዓሰርተ" + digit, no conjunction: ዓሰርተ ሓደ … ዓሰርተ ትሽዓተ.
- **Tens:** ዕስራ, ሰላሳ, ኣርብዓ, ሓምሳ, ስሳ, ሰብዓ, ሰማንያ, ተስዓ. **Accept:** እስራ, ሱሳ, ቴስዓ.
- **21–99:** "-ን" on both the tens and the units: 21 → "ዕስራን ሓደን", 35 → "ሰላሳን ሓሙሽተን", 99 → "ተስዓን ትሽዓተን".
- **Scales:** ሚእቲ (ሚእት before a suffix), ሺሕ, ሚልዮን, ቢልዮን ⇒ maxval 10¹². **Accept:** ሽሕ, ሺ, ሚሊዮን, ቢሊዮን.
- **Larger compounds (formal form is the default):** components from the largest scale down, with "-ን" on every component: 101 → "ሚእትን ሓደን", 125 → "ሚእትን ዕስራን ሓሙሽተን", 1500 → "ሺሕን ሓሙሽተ ሚእትን", 2026 → "ክልተ ሺሕን ዕስራን ሽዱሽተን". A number that is a single component (5, 20, 200, 5000) takes no "-ን". **No "ሓደ" before any scale word (author):** 100 → "ሚእቲ", 1000 → "ሺሕ", 10⁶ → "ሚልዮን", 10⁹ → "ቢልዮን". **Teens (author):** a teen is one block: it never takes "-ን" inside, and inside a larger number "-ን" goes once, on its last word: 2015 → "ክልተ ሺሕን ዓሰርተ ሓሙሽተን", 615 → "ሽዱሽተ ሚእትን ዓሰርተ ሓሙሽተን", 812 → "ሸሞንተ ሚእትን ዓሰርተ ክልተን". Compare 2025 → "ክልተ ሺሕን ዕስራን ሓሙሽተን". "ዓሰርተን ሓሙሽተን" is wrong and is not produced.
- **Accept:** every "-ን" pattern (on every component, only the last tens and units, first only, none); "ን" written as a separate word ("ዕስራ ን ሓሙሽተ"); a scale word with "ሓደ" before it ("ሓደ ሚእቲ", "ሓደ ሚልዮን"); "ዓሰርተ ሓሙሽተ ሚእቲ" (fifteen hundred).
- **Years:** ordinary cardinals.
- **Ordinals:** 1st–10th use the dedicated words with gender (masculine default; `gender="f"` for feminine): ቀዳማይ/ቀዳመይቲ, ካልኣይ/ካልአይቲ, ሳልሳይ/ሳልሰይቲ, ራብዓይ/ራብዐይቲ, ሓምሻይ/ሓምሸይቲ, ሳድሳይ/ሳድሰይቲ, ሳብዓይ/ሳብዐይቲ, ሳምናይ/ሳምነይቲ, ታስዓይ/ታስዐይቲ, ዓስራይ/ዓስረይቲ. From 11 up: "መበል" + cardinal. **Accept:** "መበል" + any cardinal including 1–10, and "መበል" + a dedicated word.
- **Numeric ordinal (author):** 1–10 is the digit + "ይ" ("1ይ", "10ይ"). From 11 up it is "መበል" + the digits ("መበል 11", "መበል 100"). Feminine 1–10 is digit + "ይቲ" *(my call, from Gemini; the author's rules don't mention gender here)*. **Accept:** a hyphen before the suffix ("3-ይ").
- **Negative word (author):** ኣሉታ. **Accept:** ኣሉታዊ, ሚነስ, ኔጌቲቭ.
- **Point word:** ነጥቢ.
- **Currency (author: no "-ን" on the unit words):** amount, unit word, sub-amount, sub-unit word, side by side; the amounts themselves follow the number rules above. 12.50 birr → "ዓሰርተ ክልተ ብር ሓምሳ ሳንቲም", 21.25 birr → "ዕስራን ሓደን ብር ዕስራን ሓሙሽተን ሳንቲም". Currencies: ETB (ብር), USD (ዶላር), EUR (ዩሮ), ERN (ናቕፋ), all with ሳንቲም as the sub-unit (author). **Accept:** ሳንቲም and ሰንት for any currency, "ምስ" between the parts, "-ን" on the unit words, and a trailing ጥራይ/ጥራሕ ("only").

### Afaan Oromoo (`om`), Qubee (Latin)

The author has Gemini review all Oromo output.

- **Digits:** zeeroo, tokko, lama, sadii, afur, shan, ja'a, torba, saddeet, sagal, kudhan. **Accept:** duwwaa, jaha/jaa, sadi, the vowel-final spoken forms (afuri, shani, sagali …), saddet.
- **Teens:** "kudha" + digit, two words, no conjunction. **Accept:** written as one word, hyphenated, and "kudhan fi" + digit.
- **Tens:** digdama, soddoma, afurtama, shantama, jaatama, torbaatama, saddeettama, sagaltama. **Accept:** jahaatama.
- **21–99:** the tens word's final "-a" becomes "-ii": "digdamii tokko", "soddomii shan", "sagaltamii sagal". **Accept:** "digdama tokko", "digdama fi tokko".
- **Scales:** dhibba, kuma, miiliyoona, biiliyoona ⇒ maxval 10¹². **Accept:** miliyoona, biliyoona, and the forms in the Gemini file.
- **Word order (author):** the scale word comes first: "dhibba lama" = 200, "kuma shan" = 5000. **Accept** the reversed order ("lama kuma") only where the phrase cannot be read in the default order; the default reading always wins. So "kuma lama dhibba shan" is 2500.
- **Default compound:** explicit "tokko"; components from the largest scale down; "fi" only before the final component, with no vowel lengthening: 101 → "dhibba tokko fi tokko", 125 → "dhibba tokko fi digdamii shan", 1500 → "kuma tokko fi dhibba shan", 2026 → "kuma lama fi digdamii ja'a", 5327 → "kuma shan dhibba sadii fi digdamii torba". The author's sample writes a comma after "kuma shan". Output has no comma *(my call; a comma in an ASR transcript gets in the way)*. **Accept:** a comma, "fi" between every component or none, the lengthened forms ("tokkoo fi", "lamaa fi"), and the scale word without "tokko".
- **Years:** ordinary cardinals. `to_number(..., to="year")` also accepts the two-part form "digdamii kudha shan" = 2015. In `cardinal` mode that phrase is not one number.
- **Ordinals:** "-ffaa" after a vowel, "-affaa" after a consonant: tokkoffaa, lamaffaa, sadaffaa, arfaffaa, shanaffaa, kurnaffaa (10th), dhibbaffaa. **Accept:** lammaffaa, afraffaa, kudhaffaa, and the forms in the Gemini file. Numeric: digits + "ffaa" ("3ffaa").
- **Negative / point:** negaatiivii (accept hir'uu, minus, maayinasii), tuqaa (accept qabxii).
- **Currency:** ETB (qarshii, saantima; accept birrii/birr), USD (doolaara, seentii), EUR (yuuroo). Default order: amount then unit. Accept the unit before the amount ("qarshii shantama").

## Verification

- **Hand-written tests per language and per mode,** with expected strings taken from this document. The author signs off on the test tables for Amharic and Tigrinya.
- **Round-trip property test:** `to_number(to_words(n, lang, to=m), lang, to=m) == n` over 0–10,000 exhaustively, plus random larger values up to maxval, for every language and mode.
- **Variant acceptance tests:** each "Accept" item above has at least one case.
- **Black-box comparison with num2words2 (dev-only, not a test dependency):** a script in `scripts/` that runs num2words2 built from its GitHub source over a range of values and prints every difference from our output, for the author to review. Building it needs a Rust toolchain and several GB of disk for Cargo's build output, so point `CARGO_TARGET_DIR` at a disk with room. Expected differences are listed so the rest stand out. As of commit a7bde8c these are:
  - **am:** "መቶ" for 100 and "አስራ" for 16; ሰልቢ for negative.
  - **ti:** "ን" as a separate word, put on teens, and not on the last part; ሽሕ rather than ሺሕ.
  - **om:** multiplier-first order; "fi" between every level; "kudhan fi" teens; "digdama fi" instead of "digdamii"; no explicit "tokko"; "sadiiffaa"; "minus".

## Left to the builder

Internal structure, helper names, how variant tables are laid out, tokenizer details, and error messages. Documentation: a README section with examples, in the style of the existing ones, and a `docs/number_words.md` table of the word lists.

## Roadmap (not in v1)

1. **Running text, both directions.** Digits → words inside a sentence ("በ2015 ዓ.ም" → "በሁለት ሺህ አሥራ አምስት ዓ.ም"), and number phrases → digits inside a sentence, including ordinals ("ሁለተኛ" → "2ኛ") and money. **Author's requirement:** prefixes and suffixes attached to a number word are recognized and kept exactly as written ("በሁለት" → "በ2", "ሁለቱ" → "2ቱ", Tigrinya "ሺሕን"). Text that is not a number stays byte-for-byte as it was.
2. Phone numbers read digit by digit.
3. Times.
4. Ge'ez numerals in running text.
5. Ethiopian-calendar date phrases.
