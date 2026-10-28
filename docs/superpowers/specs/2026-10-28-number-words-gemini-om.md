# Gemini on Afaan Oromoo numbers (2026-10-28, raw answer)

Here is a complete, linguistically grounded guide for Afaan Oromoo (Qubee) number normalization for ASR (number-to-words canonical generation and words-to-number acoustic mapping).

---

### 1. Basic Numbers & Variants

#### 0 – 10
* **0**: `zeeroo` *(standard/most common)*; `duwwaa` *(native word: "empty/blank")*.
* **1**: `tokko` *(informal variant: `toko`)*.
* **2**: `lama`.
* **3**: `sadii` *(variants: `sadi`, `sadiyi`)*.
* **4**: `afur` *(spoken variant: `afuri`)*.
* **5**: `shan` *(spoken variant: `shani`)*.
* **6**: `ja'a` *(Central/Western standard)*; `jaha` *(Eastern/Hararghe standard, extremely common in ASR)*; `jaa` *(colloquial)*.
* **7**: `torba` *(variant: `tolba` in southern Borana)*.
* **8**: `saddeet` *(variants: `saddet`, `saddeeti`)*.
* **9**: `sagal` *(variant: `sagali`)*.
* **10**: `kudhan` *(variant: `kudhani`; collective: `kurnan`)*.

#### 11 – 19 (`kudha` style)
The prefix is `kudha` (shortened form of *kudhan*). Standard orthography separates words with a space:
* **11**: `kudha tokko`
* **12**: `kudha lama`
* **13**: `kudha sadii`
* **14**: `kudha afur`
* **15**: `kudha shan`
* **16**: `kudha ja'a` / `kudha jaha`
* **17**: `kudha torba`
* **18**: `kudha saddeet`
* **19**: `kudha sagal`
*(ASR variants to accept: compound forms without space like `kudhatokko`, hyphenated `kudha-tokko`, or archaic/spoken `kudhanii tokko` / `kudhani fi tokko`)*.

#### Tens (20 – 90)
* **20**: `digdama` *(Western spoken assimilation: `diddama`)*.
* **30**: `soddoma`.
* **40**: `afurtama` *(metathesis variant: `arfattama`)*.
* **50**: `shantama`.
* **60**: `jaatama` / `jahaatama` *(variants: `ja'atama`, `jahatama`)*.
* **70**: `torbaatama` *(variant: `torbatama`)*.
* **80**: `saddeettama` *(variant: `saddettama`)*.
* **90**: `sagaltama`.

#### Scales ($10^2$ to $10^9$)
* **100 ($10^2$)**: `dhibba` *(or `dhibba tokko`)*.
* **1,000 ($10^3$)**: `kuma` *(or `kuma tokko`)*.
* **1,000,000 ($10^6$)**: `miliyoona` *(variants: `miliyon`, `miliyoonii`)*.
* **1,000,000,000 ($10^9$)**: `biliyoona` *(variants: `biliyon`, `biliyoonii`)*.

---

### 2. Compound Formation & Spoken Syntax

#### Tens + Units (21–99)
Formed by lengthening the final vowel of the ten into `-ii` (the natural enclitic coordinator) before the digit:
* **21**: `digdamii tokko` *(spoken variant: `digdamaa fi tokko` / `digdama fi tokko`)*
* **35**: `soddomii shan`
* **99**: `sagaltamii sagal`

#### Word Order: `dhibba lama` vs `lama dhibba`
* **Standard Oromo**: **Head + Multiplier** (`dhibba lama` = 200, `kuma lama` = 2,000, `miliyoona shan` = 5,000,000). Modifiers strictly follow nouns in Oromo syntax.
* **ASR Spoken Variant**: Under Amharic (*hulät mäto*) and English influence, urban and bilingual speakers often say the inverted order: `lama dhibba` or `lama kuma`. *Words-to-number must accept this, but number-to-words should never generate it.*

#### Dropping `tokko` before `kuma` / `dhibba`
* Both `dhibba` and `dhibba tokko` are valid for 100.
* Both `kuma` and `kuma tokko` are valid for 1,000.
* **Rule**: Accept both in ASR parser. In default text-to-number generation, use `tokko` explicitly (`kuma tokko`, `dhibba tokko`) for clarity.

#### Where `fi` ("and") is used
In standard Afaan Oromoo, `fi` (often causing the preceding vowel to lengthen: `-oo fi` or `-aa fi`) connects scale blocks:
* Between scales: `kuma tokkoo fi dhibba lama` (1,200).
* Before the final compound: `kuma tokko dhibba lamaa fi soddomii afur` (1,234).
* In fast speech, `fi` is frequently dropped entirely.

#### Examples & Spoken Variants:
* **1234**:
  * *Canonical written*: `kuma tokko dhibba lamaa fi soddomii afur` (or `kuma tokkoo fi dhibba lamaa fi soddomii afur`)
  * *Spoken variants*:
    - `kuma dhibba lama soddomii afur` *(dropping `tokko` and `fi`)*
    - `kuma tokko dhibba lama soddomaa fi afur`
    - `tokko kuma lama dhibba soddomii afur` *(Amharic calque order)*
* **1500**:
  * *Canonical written*: `kuma tokkoo fi dhibba shan`
  * *Spoken variants*:
    - `kuma fi dhibba shan` / `kuma dhibba shan`
    - `dhibba kudha shan` *(literally "15 hundreds" — standard Oromo order: unit + multiplier)*
    - `kudha shan dhibba` *(Amharic calque: "asra ammest mäto" / fifteen hundred)*
    - `kuma tokkoofi walakkaa` *(commerce/market style: "one thousand and a half")*
* **2015 (Year / Bara 2015)**:
  * *Canonical formal*: `kuma lamaa fi kudha shan` (or `bara kuma lamaa fi kudha shan`)
  * *Spoken variants*:
    - `kuma lama kudha shan` *(dropping `fi`)*
    - `digdamii kudha shan` *(colloquial 2-digit year grouping: "twenty fifteen", very common in radio and street speech)*
    - `lama kuma kudha shan` *(inverted modifier calque)*

---

### 3. Ordinal Numbers

#### Formation Rules
Formed by appending **`-ffaa`** (if ending in a vowel) or **`-affaa`** (if ending in a consonant):
* **1st**: `tokkoffaa`
* **2nd**: `lammaffaa` *(note gemination: `m` $\rightarrow$ `mm`)*
* **3rd**: `sadaffaa` *(vowel shift: `sadii` $\rightarrow$ `sada-` + `-ffaa`)*
* **4th**: `arfaffaa` *(metathesis variant: `afraffaa`)*
* **5th**: `shanaffaa` *(epenthetic `-a-` before consonant stem)*
* **6th**: `ja'affaa` / `jahaffaa`
* **7th**: `torbaffaa`
* **8th**: `saddeettaffaa` *(variant: `saddeetaffaa`)*
* **9th**: `sagalaffaa` *(variant: `saglaffaa`)*
* **10th**: `kurnaffaa` *(regularized variant: `kudhaffaa`)*
* **20th+**: `digdammaffaa` (or `digdamaffaa`), `soddomaffaa`, etc.

#### Irregular / Semantic Equivalents:
* **1st**: `jalqaba` / `jalqabaa` *(beginning/first)*, `dura` / `duraa` *(former/prior/first)*, `hangafa` *(first-born/senior)*.
* **2nd**: `ittiaanaa` / `itti-aanaa` *(next/second/deputy)*.

#### Numeric Ordinal Abbreviation:
* Standard: **`1ffaa`**, **`2ffaa`**, **`3ffaa`** *(digits directly concatenated with `ffaa`)*.
* Variants found in print: `1^ffaa`, `1-ffaa`, and occasionally `1ffa` (single `f`).

---

### 4. Negative & Decimal Point Words

* **Negative (-)**:
  * *Standard educational/scientific*: `negaatiivii` (e.g., -5 = `negaatiivii shan`).
  * *Native mathematical*: `hir'uu` (e.g., `hir'uu shan`).
  * *ASR spoken variants*: `hir'isa` *(minus)*, `maayinasii` / `maayinesii` *(English loan)*.
  * *(Uncertain/rare)*: `wawwee` / `lakkoofsa wawwee` is coined in linguistic terminologies for negative integers, but virtually never occurs in spontaneous natural speech.
* **Decimal Point (.)**:
  * *Standard canonical*: `tuqaa` (e.g., 3.14 = `sadii tuqaa tokko afur`).
  * *ASR spoken variants*: `qabxii` *(calqued from Amharic näṭǝb)*, `poyintii` *(English loan)*.

---

### 5. Currencies

* **Birr / Santim**:
  * Birr: `qarshii` *(standard canonical default)*. Spoken variants: `birrii`, `birr`.
  * Santim: `saantima` *(canonical default)* / `saantimii`.
  * *Order*: Usually `qarshii [number]` (e.g. `qarshii shantama`), though `shantama qarshii` occurs colloquially.
* **Dollar / Cent**:
  * Dollar: `doolaara` *(canonical)* / `doolarii`.
  * Cent: `seentii` *(canonical)* / `saantima` *(colloquial)*.
* **Euro**:
  * Euro: `yuuroo` *(canonical default)*. Variants: `awuroo`, `yuroo`.

---

### 6. Recommended Default Written Form for Compounds

For **number-to-words (canonical/default)**, adhere to standard curriculum orthography:
1. **Separated words** for teens: `kudha tokko` (not `kudhatokko`).
2. **Coordinating vowel `-ii`** for tens + units: `digdamii tokko`, `shantamii shan` (not `digdama fi tokko`).
3. **Explicit `tokko`** for 100 and 1,000: `dhibba tokko`, `kuma tokko`.
4. **Strict Head-First Order**: `kuma [N]`, `dhibba [N]` (never `[N] kuma`).
5. **Connecting `fi` with vowel lengthening (`-oo fi`)** before the last segment:
   * **1234** $\rightarrow$ `kuma tokko dhibba lamaa fi soddomii afur`
   * **1500** $\rightarrow$ `kuma tokkoo fi dhibba shan`
   * **2015 (Year)** $\rightarrow$ `kuma lamaa fi kudha shan` *(or prefixed with `bara ...` if normalized with context)*.
