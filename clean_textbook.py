"""
Script to clean textbook data.
Remove certain troublesome lines.
"""
import re
import sys


def main():
    YEAR_CITATION_REGEX = re.compile(r"\(\d\d\d\d\)")
    HAS_LETTERS = re.compile(r"[A-Za-z]+")
    text_path_in = sys.argv[1]
    text_path_out = sys.argv[2]
    with open(text_path_in, "r", encoding="utf8") as infile, open(
        text_path_out, "w", encoding="utf8"
    ) as outfile:
        for line in infile:
            if (
                YEAR_CITATION_REGEX.findall(line)
                or not HAS_LETTERS.findall(line)
                or len(line.split()) <= 1
            ):
                continue
            outfile.write(line)


if __name__ == "__main__":
    main()
