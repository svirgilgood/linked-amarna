#!/usr/bin/env python3
"""Find names in Amarna Text"""

import re
import sys

import pandas as pd

DIGI_RE = re.compile(r"(\d{3}:[LR\d]{3,4}) ")


def rgroup(*choices):
    """grouping options for regex"""
    return "(" + "|".join(choices) + ")"


def rany(*choices):
    """any of the options"""
    return rgroup(*choices) + "*"


def maybe(*choices):
    """any of the options"""
    return rgroup(*choices) + "?"


def some(*choices):
    """some of the matches possible choices"""
    return rgroup(*choices) + "+"


def name_gen():
    """Generate the name finder"""
    denominative = r"(^| )[\[\]]?" + r"(m|f)" + r"[\[\]]?" + r"\."
    syllable = r"[\w0-9$\{\}\[\]<>]+"
    syllable_divider = rgroup(r"-", r"\.")
    name = (
        denominative
        + rgroup(syllable, maybe(syllable_divider))
        + rany(syllable, maybe(syllable_divider))
        # # # + rany(syllable, maybe(syllable_divider))
    )

    return name


def text_cleaner(text):
    """cleaning the text to make it more fitting for unicode comparisons"""
    return text.translate(
        {
            ord("]"): "",
            ord("["): "",
            ord("}"): "",
            ord("{"): "",
            ord("<"): "",
            ord(">"): "",
            ord("$"): "š",
            ord("ß"): "Š",
            ord("µ"): "ṭ",
            ord("@"): "ʾ",
            ord("c"): "ṣ",
            ord("C"): "Ṣ",
        }
    )


def name_parser(text_list, name_re):
    """Name parser, returns a list of references and names
    """
    references = []
    for text in text_list:
        try:
            _, reference, line = DIGI_RE.split(text)
        except ValueError:
            continue
        try:
            matches = name_re.finditer(line)
            for match in matches:
                name = match.group()
                references.append(
                    {
                        "reference": reference,
                        "text": line,
                        "name": name,
                        "normalized": text_cleaner(name),
                    }
                )
        except AttributeError:
            continue

    return references


def main():
    """here is the name """
    with open(sys.argv[1]) as file_p:
        text = file_p.read()
    text = text.split("\n")
    re_name = name_gen()
    name_pattern = re.compile(re_name)
    references = name_parser(text, name_pattern)
    dataframe = pd.DataFrame(references)
    dataframe.to_excel("AmarnaNames2.xlsx")


if __name__ == "__main__":
    main()
