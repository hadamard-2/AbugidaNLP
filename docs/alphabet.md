# Alphabets for Amharic and Tigrinya

This note records how we decided which letters belong to the Amharic and Tigrinya alphabets.

## Source

We use the exemplar characters in the Unicode CLDR locale data (release 49, October 2026) as the authority for which letters each language uses. CLDR is maintained by the Unicode Consortium and is what operating systems and ICU use for locale data. We first looked at a learner's chart (mesmertigrinya.com), but rejected it as a source because it disagrees with CLDR and cites nothing.

## Letter families

| Locale | CLDR status | Letter families | Notes |
|---|---|---|---|
| `am` (Amharic) | approved | 34 | Includes ሠ, ኀ, ፀ and ቨ; no ቐ |
| `ti` (Tigrinya; Ethiopian Tigrinya inherits it) | approved | 35 | All 34 Amharic families plus ቐ |
| `ti_ER` (Eritrean Tigrinya) | unconfirmed | 32 | ሠ and ፀ moved to the auxiliary (rarely used) set; no ጰ |

"Letter families" counts base rows, not the separate labialized (w-form) rows. Tigrinya also has the labialized rows of ቐ (ቘ…) and ኸ (ዀ…), which Amharic lacks.

Amharic charts sometimes say 33 instead of 34; the difference is usually ቨ, which was added for the "v" sound in loanwords.

## Open-o letters

The open-o letters (ሇ ቇ ኇ ጏ ፇ) are in the auxiliary set for Tigrinya (`ti` lists ፇ in its main set, likely a data quirk) and absent from Amharic. They were added in Unicode 4.1 for languages such as Me'en, Mursi and Suri.

## Sources

- Unicode CLDR 49: [`am.xml`](https://github.com/unicode-org/cldr/blob/release-49/common/main/am.xml), [`ti.xml`](https://github.com/unicode-org/cldr/blob/release-49/common/main/ti.xml), [`ti_ER.xml`](https://github.com/unicode-org/cldr/blob/release-49/common/main/ti_ER.xml)
- [Unicode DerivedAge.txt](https://www.unicode.org/Public/UCD/latest/ucd/DerivedAge.txt) (the open-o letters were added in Unicode 4.1)
