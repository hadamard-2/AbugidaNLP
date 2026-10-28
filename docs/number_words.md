# Number words

The word lists used by `NumberWordConverter` for Amharic, Tigrinya and Afaan Oromoo.

The tables below were generated from `abugida/number_words/tables.py`. The default word is what `to_words` writes. The accepted variants are extra spellings that `to_number` also reads, in addition to the grammar variants (optional leading "one", conjunction patterns, word order) that are not word lists.

## Amharic (`am`)

### Default words

Digits:

| Value | Word |
|---|---|
| 0 | ዜሮ |
| 1 | አንድ |
| 2 | ሁለት |
| 3 | ሦስት |
| 4 | አራት |
| 5 | አምስት |
| 6 | ስድስት |
| 7 | ሰባት |
| 8 | ስምንት |
| 9 | ዘጠኝ |
| 10 | አሥር |

Teens (11-19) are the teens prefix `አሥራ` followed by the digit word.

Tens:

| Value | Word |
|---|---|
| 20 | ሃያ |
| 30 | ሠላሳ |
| 40 | አርባ |
| 50 | ሃምሳ |
| 60 | ስድሳ |
| 70 | ሰባ |
| 80 | ሰማንያ |
| 90 | ዘጠና |

Scales:

| Value | Word |
|---|---|
| 100 | መቶ |
| 1,000 | ሺህ |
| 1,000,000 | ሚሊዮን |
| 1,000,000,000 | ቢሊዮን |
| 1,000,000,000,000 | ትሪሊዮን |

Other words:

| Item | Word |
|---|---|
| Negative | ኔጌቲቭ |
| Point | ነጥብ |
| Currency joiner | ከ |

Currencies:

| Code | Unit | Sub-unit |
|---|---|---|
| ETB | ብር | ሳንቲም |
| USD | ዶላር | ሳንቲም |

Ordinal words:

The ordinal is the cardinal with the last word replaced by its ordinal form.

| Cardinal word | Ordinal word |
|---|---|
| አንድ | አንደኛ |
| ሁለት | ሁለተኛ |
| ሦስት | ሦስተኛ |
| አራት | አራተኛ |
| አምስት | አምስተኛ |
| ስድስት | ስድስተኛ |
| ሰባት | ሰባተኛ |
| ስምንት | ስምንተኛ |
| ዘጠኝ | ዘጠነኛ |
| አሥር | አሥረኛ |
| ሃያ | ሃያኛ |
| ሠላሳ | ሠላሳኛ |
| አርባ | አርባኛ |
| ሃምሳ | ሃምሳኛ |
| ስድሳ | ስድሳኛ |
| ሰባ | ሰባኛ |
| ሰማንያ | ሰማንያኛ |
| ዘጠና | ዘጠናኛ |
| መቶ | መቶኛ |
| ሺህ | ሺህኛ |
| ሚሊዮን | ሚሊዮንኛ |
| ቢሊዮን | ቢሊዮንኛ |
| ትሪሊዮን | ትሪሊዮንኛ |

### Accepted variants

The parser accepts these in addition to the default words.

| Variant | Reads as |
|---|---|
| ባዶ | ዜሮ |
| አንዲት | አንድ |
| አምሳ | ሃምሳ |
| ኃምሳ | ሃምሳ |
| ሀምሳ | ሃምሳ |
| ስልሳ | ስድሳ |
| ሺ | ሺህ |
| ሲቀነስ | ኔጌቲቭ |
| አሉታዊ | ኔጌቲቭ |
| መጀመሪያ | አንደኛ |
| ሺኛ | ሺህኛ |

## Tigrinya (`ti`)

### Default words

Digits:

| Value | Word |
|---|---|
| 0 | ባዶ |
| 1 | ሓደ |
| 2 | ክልተ |
| 3 | ሰለስተ |
| 4 | ኣርባዕተ |
| 5 | ሓሙሽተ |
| 6 | ሽዱሽተ |
| 7 | ሸውዓተ |
| 8 | ሸሞንተ |
| 9 | ትሽዓተ |
| 10 | ዓሰርተ |

Teens (11-19) are the teens prefix `ዓሰርተ` followed by the digit word.

Tens:

| Value | Word |
|---|---|
| 20 | ዕስራ |
| 30 | ሰላሳ |
| 40 | ኣርብዓ |
| 50 | ሓምሳ |
| 60 | ስሳ |
| 70 | ሰብዓ |
| 80 | ሰማንያ |
| 90 | ተስዓ |

Scales:

| Value | Word | Form before the conjunction suffix |
|---|---|---|
| 100 | ሚእቲ | ሚእት |
| 1,000 | ሺሕ |  |
| 1,000,000 | ሚልዮን |  |
| 1,000,000,000 | ቢልዮን |  |

Other words:

| Item | Word |
|---|---|
| Negative | ኣሉታ |
| Point | ነጥቢ |
| Conjunction | ን |
| Ordinal prefix (11 and up) | መበል |

Currencies:

| Code | Unit | Sub-unit |
|---|---|---|
| ETB | ብር | ሳንቲም |
| USD | ዶላር | ሳንቲም |
| EUR | ዩሮ | ሳንቲም |
| ERN | ናቕፋ | ሳንቲም |

Ordinal words:

Dedicated words for 1st to 10th. From 11th up the ordinal is the prefix and the cardinal.

| Value | Masculine | Feminine |
|---|---|---|
| 1 | ቀዳማይ | ቀዳመይቲ |
| 2 | ካልኣይ | ካልአይቲ |
| 3 | ሳልሳይ | ሳልሰይቲ |
| 4 | ራብዓይ | ራብዐይቲ |
| 5 | ሓምሻይ | ሓምሸይቲ |
| 6 | ሳድሳይ | ሳድሰይቲ |
| 7 | ሳብዓይ | ሳብዐይቲ |
| 8 | ሳምናይ | ሳምነይቲ |
| 9 | ታስዓይ | ታስዐይቲ |
| 10 | ዓስራይ | ዓስረይቲ |

Numeric ordinals: 1-10 take the suffix `ይ` (feminine `ይቲ`) after the digits; 11 and up are the prefix and the digits.

### Accepted variants

The parser accepts these in addition to the default words.

| Variant | Reads as |
|---|---|
| ዜሮ | ባዶ |
| ሓንቲ | ሓደ |
| ሽድሽተ | ሽዱሽተ |
| ሸድሽተ | ሽዱሽተ |
| ሾብዓተ | ሸውዓተ |
| ሾሞንተ | ሸሞንተ |
| ተሽዓተ | ትሽዓተ |
| ትሻዓተ | ትሽዓተ |
| እስራ | ዕስራ |
| ሱሳ | ስሳ |
| ቴስዓ | ተስዓ |
| ሽሕ | ሺሕ |
| ሺ | ሺሕ |
| ሚሊዮን | ሚልዮን |
| ቢሊዮን | ቢልዮን |
| ኣሉታዊ | ኣሉታ |
| ሚነስ | ኣሉታ |
| ኔጌቲቭ | ኣሉታ |
| ሰንት | ሳንቲም |
| አርባዕተ | ኣርባዕተ |
| አርብዓ | ኣርብዓ |
| አሉታ | ኣሉታ |

Words skipped in currency phrases: `ምስ`, `ጥራይ`, `ጥራሕ`.

## Afaan Oromoo (`om`)

### Default words

Digits:

| Value | Word |
|---|---|
| 0 | zeeroo |
| 1 | tokko |
| 2 | lama |
| 3 | sadii |
| 4 | afur |
| 5 | shan |
| 6 | ja'a |
| 7 | torba |
| 8 | saddeet |
| 9 | sagal |
| 10 | kudhan |

Teens (11-19) are the teens prefix `kudha` followed by the digit word.

Tens:

| Value | Word | Word before a units word |
|---|---|---|
| 20 | digdama | digdamii |
| 30 | soddoma | soddomii |
| 40 | afurtama | afurtamii |
| 50 | shantama | shantamii |
| 60 | jaatama | jaatamii |
| 70 | torbaatama | torbaatamii |
| 80 | saddeettama | saddeettamii |
| 90 | sagaltama | sagaltamii |

Scales:

| Value | Word |
|---|---|
| 100 | dhibba |
| 1,000 | kuma |
| 1,000,000 | miiliyoona |
| 1,000,000,000 | biiliyoona |

Other words:

| Item | Word |
|---|---|
| Negative | negaatiivii |
| Point | tuqaa |
| Conjunction | fi |
| Year prefix (accepted before a year) | bara |

Currencies:

| Code | Unit | Sub-unit |
|---|---|---|
| ETB | qarshii | saantima |
| USD | doolaara | seentii |
| EUR | yuuroo | (none yet) |

Ordinal words:

Ordinals add `ffaa` after a vowel and `affaa` after a consonant, except for these irregular ones.

| Cardinal word | Ordinal word |
|---|---|
| tokko | tokkoffaa |
| lama | lamaffaa |
| sadii | sadaffaa |
| afur | arfaffaa |
| kudhan | kurnaffaa |

### Accepted variants

The parser accepts these in addition to the default words.

| Variant | Reads as |
|---|---|
| duwwaa | zeeroo |
| toko | tokko |
| sadi | sadii |
| sadiyi | sadii |
| afuri | afur |
| shani | shan |
| jaha | ja'a |
| jaa | ja'a |
| tolba | torba |
| saddet | saddeet |
| saddeeti | saddeet |
| sagali | sagal |
| kudhani | kudhan |
| kurnan | kudhan |
| diddama | digdama |
| arfattama | afurtama |
| jahaatama | jaatama |
| ja'atama | jaatama |
| jahatama | jaatama |
| torbatama | torbaatama |
| saddettama | saddeettama |
| miliyoona | miiliyoona |
| miliyon | miiliyoona |
| miliyoonii | miiliyoona |
| biliyoona | biiliyoona |
| biliyon | biiliyoona |
| biliyoonii | biiliyoona |
| hir'uu | negaatiivii |
| hir'isa | negaatiivii |
| minus | negaatiivii |
| maayinasii | negaatiivii |
| maayinesii | negaatiivii |
| qabxii | tuqaa |
| poyintii | tuqaa |
| birrii | qarshii |
| birr | qarshii |
| saantimii | saantima |
| doolarii | doolaara |
| awuroo | yuuroo |
| yuroo | yuuroo |

Ordinal variants:

| Variant | Reads as |
|---|---|
| lammaffaa | lamaffaa |
| afraffaa | arfaffaa |
| kudhaffaa | kurnaffaa |
| ja'affaa | ja'affaa |
| jahaffaa | ja'affaa |
| saddeettaffaa | saddeetaffaa |
| saglaffaa | sagalaffaa |
| digdammaffaa | digdamaffaa |

## Known behaviours

- Afaan Oromoo default forms can be ambiguous for rare large values: 900046 and 946000 both give "kuma dhibba sagal fi afurtamii ja'a". Parsing reads the string greedily as 946000.
- "kuma dhibba shan" parses as 500000 (the default reading wins, not 1500).
- "kuma digdama fi tokko" parses as 21000.
- The Tigrinya and Amharic parsers are lenient about the "ን" patterns, so more spellings of a number are accepted than the generator would write.
