#!/usr/bin/env python3
"""create and populate a table of text data for the amarna letters"""

import sqlite3

from name_greper import text_cleaner
from name_greper import DIGI_RE

CONN = sqlite3.connect("../data/amarna_name.db")
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


def populate_table(reference, line, cleaned_text):
    """populate the ea_text table with data"""
    insert_query = """
    INSERT INTO ea_texts (reference, line, cleaned_text)
    VALUES (?, ?, ?);"""
    CUR.execute(insert_query, (reference, line, cleaned_text))


def main():
    """Creating and populating a table with all of the texts in the El Amarna corpus"""
    aparser = argparse.ArgumentParser()
    aparser.add_argument(
        "-i",
        "--init",
        help="initialize the text table in the database",
        action="store_true",
    )
    args = aparser.parse_args()

    if args.init:
        create_table()

    with open("../data/ElAmarnaLetters.txt") as eafp:
        for index, line in enumerate(eafp):
            try:
                _, reference, text = DIGI_RE.split(line.strip())
                cleaned_text = text_cleaner(text)
                populate_table(reference, text, cleaned_text)
                if index % 100 == 0:
                    CONN.commit()
            except ValueError:
                pass


if __name__ == "__main__":
    import argparse

    main()
