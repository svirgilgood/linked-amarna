#!/usr/bin/env python3
"""Find names in Amarna Text, requires a single text file, or the command line
webbrowser links"""

import re
import subprocess
import sqlite3

import pandas as pd

DIGI_RE = re.compile(r"(\d{3}:[LR\d]{3,4}) ")

CONN = sqlite3.connect("test.db")
CUR = CONN.cursor()


def create_table():
    """Create the ea_text table which contains all of the texts"""
    create_query = """
    CREATE TABLE IF NOT EXISTS ea_texts (
    reference TEXT,
    line TEXT,
    cleaned_text TEXT
    );"""
    CUR.execute(create_query)
    CONN.commit()


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


def text_parser(text_list):
    """create a list of dictionaries from a list of text lines"""
    references = []
    for text in text_list:
        try:
            _, reference, line = DIGI_RE.split(text)
            references.append({"reference": reference, "text": line})
        except ValueError:
            continue
    return references


def name_parser(references, name_re):
    """Name parser, returns a list of references and names
    """
    new_references = []
    for reference in references:
        line_ref = reference["reference"]
        line = reference["text"]
        try:
            matches = name_re.finditer(line)
            for match in matches:
                name = match.group()
                new_references.append(
                    {
                        "reference": line_ref,
                        "text": line,
                        "name": name,
                        "normalized": text_cleaner(name),
                    }
                )
        except AttributeError:
            continue

    return new_references


def url_downloader():
    """Use links to download the amarna texts from the website"""
    texts = []
    urls = [
        "https://www.tau.ac.il/humanities/semitic/EA60-114.html",
        "https://www.tau.ac.il/humanities/semitic/EA115-162.html",
        "https://www.tau.ac.il/humanities/semitic/EA163-262.html",
        "https://www.tau.ac.il/humanities/semitic/EA263-end.html",
    ]
    for url in urls:
        proc = subprocess.Popen(["links", "-dump", url], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        amarna1 = out.decode()
        texts += amarna1.split("\n")
    return texts


def insert_database_query(reference, line, cleaned_text):
    """populate the ea_text table with data"""
    insert_query = """
    INSERT INTO ea_texts (reference, line, cleaned_text)
    VALUES (?, ?, ?);"""
    CUR.execute(insert_query, (reference, line, cleaned_text))


def text_database_populator(references):
    """Populate the ea_text table with the data from the corpus"""
    num = 0
    for reference in references:
        line_ref = reference["reference"]
        text = reference["text"]
        cleaned_text = text_cleaner(text)
        insert_database_query(line_ref, text, cleaned_text)
        if num % 100 == 0:
            CONN.commit()
    CONN.commit()


def main():
    """Run the command from the cli """
    aparser = argparse.ArgumentParser(
        "Create an Excel File of Amarna Names, must"
        + "specify either online or a text file"
    )

    aparser.add_argument(
        "-t", "--text", help="specify path to a plan text file from Izreel's website"
    )
    aparser.add_argument(
        "-o", "--online", help="download the website with links", action="store_true"
    )
    aparser.add_argument(
        "-i",
        "--init",
        help="initialize the text table in the database",
        action="store_true",
    )

    aparser.add_argument(
        "-d",
        "--database",
        help="populate the database with a text database. Must have table already created",
        action="store_true",
    )

    args = aparser.parse_args()

    if args.init:
        create_table()

    if args.text:
        with open(args.text) as file_p:
            text = file_p.read()
            text = text.split("\n")

    if args.online:
        text = url_downloader()
    try:
        re_name = name_gen()
        name_pattern = re.compile(re_name)
        references = text_parser(text)
        if args.database:
            text_database_populator(references)
        references = name_parser(references, name_pattern)
        dataframe = pd.DataFrame(references)
        dataframe.to_excel("AmarnaNames.xlsx")
    except UnboundLocalError:
        aparser.print_help()


if __name__ == "__main__":
    import argparse

    main()
