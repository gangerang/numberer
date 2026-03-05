#!/usr/bin/env python3
"""Generate explorer_data.js with full word enumeration for the vanity number explorer."""

import json
import os
import sys

from ranker import DIGIT_TRIE


def find_all_words(digits: str) -> list[tuple[str, int]]:
    """Return ALL (word, start_position) pairs, including same word at multiple positions."""
    results = []
    n = len(digits)
    for start in range(n):
        node = DIGIT_TRIE
        for offset in range(n - start):
            d = digits[start + offset]
            if d not in node.children:
                break
            node = node.children[d]
            for word, _ in node.words:
                results.append((word, start))
    return results


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} numbers_all.json", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        results = json.load(f)

    records = []
    total = 0
    for state, cities in results.items():
        for city, numbers in cities.items():
            for entry in numbers:
                total += 1
                raw = entry["number"]
                local = "0" + raw[2:] if raw.startswith("61") else raw
                digits9 = local[1:] if len(local) == 10 else local

                words = find_all_words(digits9)
                rec = {"n": raw, "s": state, "c": city}
                if words:
                    rec["w"] = words
                records.append(rec)

                if total % 5000 == 0:
                    print(f"  Processed {total} numbers...", file=sys.stderr)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "explorer_data.js")
    with open(out_path, "w") as f:
        f.write("const DATA = ")
        json.dump(records, f, separators=(",", ":"))
        f.write(";\n")

    print(f"Exported {len(records)} numbers to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
