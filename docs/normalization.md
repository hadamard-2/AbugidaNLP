# Normalization table

`TextNormalizer().normalize(text, language)` merges Ethiopic letters so that differently spelled forms of a word normalize to one spelling. `language` is `"am"` (Amharic) or `"ti"` (Tigrinya, both Ethiopian and Eritrean). Non-Ethiopic characters are left unchanged. The alphabet behind these rules is in [alphabet.md](alphabet.md).

## Why normalize

Letters that sound roughly the same are merged because changing one for another only rarely changes a word's meaning, and merging them makes downstream NLP tasks easier. Words where swapping such letters does change the meaning (for example ሰረቀ and ሠረቀ) should be handled with care.

The rules run in two steps. In code, both steps are composed into one translation table per language, so every letter maps directly to its final form and the result does not change if normalized again.

## Step 1: family merges (form for form)

| Rule | Mapping | Amharic | Tigrinya |
|---|---|---|---|
| ሐ → ሀ | ሐ ሑ ሒ ሓ ሔ ሕ ሖ → ሀ ሁ ሂ ሃ ሄ ህ ሆ | ✓ | ✓ |
| ኀ → ሀ | ኀ ኁ ኂ ኃ ኄ ኅ ኆ → ሀ ሁ ሂ ሃ ሄ ህ ሆ | ✓ | ✓ |
| ኋ → ሗ | ኋ → ሗ | ✓ | ✓ |
| ዐ → አ | ዐ ዑ ዒ ዓ ዔ ዕ ዖ → አ ኡ ኢ ኣ ኤ እ ኦ | ✓ | ✓ |
| ሠ → ሰ | ሠ ሡ ሢ ሣ ሤ ሥ ሦ ሧ → ሰ ሱ ሲ ሳ ሴ ስ ሶ ሷ | ✓ | ✓ |
| ፀ → ጸ | ፀ ፁ ፂ ፃ ፄ ፅ ፆ → ጸ ጹ ጺ ጻ ጼ ጽ ጾ | ✓ | ✓ |
| ኸ → ሀ (Amharic) | ኹ ኺ ኻ ኼ ኽ ኾ → ሁ ሂ ሃ ሄ ህ ሆ (ኸ itself unchanged) | ✓ | |
| ኸ → ሀ (Tigrinya) | ኸ ኹ ኺ ኻ ኼ ኽ ኾ → ሀ ሁ ሂ ሃ ሄ ህ ሆ | | ✓ |
| ዃ → ሗ | ዃ → ሗ | | ✓ |
| ኧ → አ | ኧ → አ | | ✓ |
| ቐ → ቀ | ቐ ቑ ቒ ቓ ቔ ቕ ቖ ቛ → ቀ ቁ ቂ ቃ ቄ ቅ ቆ ቋ | | ✓ |

## Step 2: 4th form into 1st form (Amharic only)

In Amharic, the 1st and 4th forms of these letters sound the same. In Tigrinya, native speakers we consulted distinguish the 1st and 4th forms of ሀ, ሐ, ኀ, አ and ዐ, so Tigrinya keeps them apart.

| Mapping |
|---|
| ሃ → ሀ |
| ኣ → አ |

After step 1 only the ሀ and አ families remain among the throat letters, so these two merges cover them. Running this step second also catches letters that step 1 maps to a 4th form, such as ኻ → ሃ → ሀ and ዓ → ኣ → አ.

## Left unchanged

| Letters | Amharic | Tigrinya |
|---|---|---|
| Open-o letters ሇ ቇ ኇ ጏ ፇ | ✓ | ✓ |
| Labialized ኀ forms ኈ ኊ ኌ ኍ | ✓ | ✓ |
| ኸ | ✓ | |
| ኧ | ✓ | |
| Labialized ቐ forms ቘ ቚ ቜ ቝ | (not used) | ✓ |
| Labialized ኸ forms ዀ ዂ ዄ ዅ | (not used) | ✓ |

## Results by language

| Merged letters | Amharic | Tigrinya |
|---|---|---|
| ሀ ሃ ሐ ሓ ኀ ኃ ኻ (Ti: also ኸ) | ሀ | ሀ (ሀ ሐ ኀ ኸ) and ሃ (ሃ ሓ ኃ ኻ) |
| አ ኣ ዐ ዓ (Ti: also ኧ) | አ | አ (አ ዐ ኧ) and ኣ (ኣ ዓ) |
| ኋ (Ti: also ዃ) | ሗ | ሗ |

## Decisions and their reasons

- **The ኸ family follows Yacob's String-Equivalence-Amharic** for Amharic: its non-1st forms join the ሀ family. For Tigrinya the whole family joins ሀ.
- **ኋ → ሗ**: the labialized ኀ "wa" form joins the labialized ሐ one. Unicode names ሗ "HHWA" although it fills the same slot as ኋ "XWAA".
- **ቐ → ቀ covers only the 7 vowel forms and ቛ**, the "wa" form; ቘ ቚ ቜ ቝ are left unchanged.
- **Out of scope:** merging labialized spellings with plain ones (ቈ/ቆ, ኰ/ኮ, ጐ/ጎ, ቍ/ቁ, ኵ/ኩ, ጕ/ጉ), rewriting spelled-out w-sounds (ቡዋ → ቧ), and producing every equivalent spelling instead of one normalized form.
