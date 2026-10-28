"""
Compare NumberWordConverter output with num2words2, for review by the author.

This is a development aid and is not used by the tests or installed with the library.

Setup:
    Install num2words2 from its GitHub source (not the older PyPI release, which gives romanized
    Tigrinya). Building it needs a Rust toolchain and several GB of disk for Cargo's build
    output, so point CARGO_TARGET_DIR at a disk with room before installing.

Usage:
    python scripts/compare_num2words2.py --lang am --to cardinal --start 0 --stop 2101

Every value where the two outputs differ is printed as "value | ours | theirs", followed by
the number of differences out of the total.

Differences expected as of num2words2 commit a7bde8c:
    am: "መቶ" for 100 and "አስራ" for 16; ሰልቢ for negative.
    ti: "ን" as a separate word, put on teens, and not on the last part; ሽሕ rather than ሺሕ.
    om: multiplier-first order; "fi" between every level; "kudhan fi" teens; "digdama fi"
        instead of "digdamii"; no explicit "tokko"; "sadiiffaa"; "minus".
Where num2words2 differs from the design, the design wins.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from abugida import NumberWordConverter  # noqa: E402

try:
    from num2words2 import num2words
except ImportError:
    print(
        "num2words2 is not installed. Install it from its GitHub source, with CARGO_TARGET_DIR "
        "set to a disk with several GB free, then run this script again.",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare our number words with num2words2.")
    parser.add_argument("--lang", required=True, choices=["am", "ti", "om"])
    parser.add_argument("--to", default="cardinal", help="mode: cardinal, ordinal, ordinal_num, year or currency")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, default=2101, help="exclusive upper bound")
    args = parser.parse_args()

    converter = NumberWordConverter()
    differences = 0
    total = 0
    for value in range(args.start, args.stop):
        total += 1
        try:
            ours = converter.to_words(value, args.lang, to=args.to)
        except Exception as error:
            ours = f"<{type(error).__name__}: {error}>"
        try:
            theirs = num2words(value, lang=args.lang, to=args.to)
        except Exception as error:
            theirs = f"<{type(error).__name__}: {error}>"
        if ours != theirs:
            differences += 1
            print(f"{value} | {ours} | {theirs}")
    print(f"{differences} differences out of {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
