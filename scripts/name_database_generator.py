#!/usr/bin/env python3
"""
This script creates, and fills the relational database used for other parts of the code.
It relies on the yaml file as well as a csv exported from OpenRefine
"""

import sqlite3
import csv
import yaml


CONN = sqlite3.connect("amarna_name.db")
CUR = CONN.cursor()


def table_creator():
    """
    Create the tables (if they don't exist) for all of the names.
    Another table might need to be created for the Locations as well
    """
    # names_and_context: Columns based on the name as it was extracted from which text
    CUR.execute(
        """
    CREATE TABLE IF NOT EXISTS names_and_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT,
    line TEXT,
    extracted_name TEXT,
    normalized_name TEXT,
    cluster_key_collision TEXT,
    cluster_levenshtein TEXT,
    cluster_levenshtein_radius2 TEXT,
    cluster_levenshtein_block5 TEXT,
    name_id INTEGER
    );"""
    )
    # canonical_names: The names as they appear in Moran
    CUR.execute(
        """
    CREATE TABLE IF NOT EXISTS canonical_names (
    name_id INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name TEXT,
    scope_note TEXT,
    language TEXT,
    city_id INTEGER,
    associated_city TEXT
    );"""
    )
    # name_variants: The possible name variants
    CUR.execute(
        """
    CREATE TABLE IF NOT EXISTS name_variants (
    name_id INTEGER,
    name_variant TEXT,
    source TEXT
    );"""
    )
    # related_terms: which terms are related to the names
    CUR.execute(
        """
    CREATE TABLE IF NOT EXISTS related_terms (
    name_id INTEGER,
    relation TEXT,
    related_id INTEGER,
    related_item TEXT
    );"""
    )
    CONN.commit()


def sql_importfunctions(name_dict, num):
    """Runs the import queries for each of the items int he name_dict"""
    for name, item_dict in name_dict.items():
        print(name)
        # Columns: canonical_name, scope_note, language, city_id, associated_city
        CUR.execute(
            """
        INSERT INTO canonical_names (canonical_name)
        VALUES (?)""",
            (name,),
        )
        name_id = CUR.lastrowid

        item_processor = {
            "LA": {"table_name": "canonical_names", "column": "language",},
            "SN": {"table_name": "canonical_names", "column": "scope_note",},
        }
        query = '''UPDATE {}
        SET {} = "{}"
        WHERE name_id = {}
        AND canonical_name = "{}"'''

        for key, items in item_dict.items():
            if key == "UF":
                for item in items:
                    var_query = "INSERT INTO name_variants (name_id, name_variant) VALUES (?, ?)"
                    CUR.execute(var_query, (name_id, item))
            else:
                try:
                    table_name = item_processor[key]["table_name"]
                    column = item_processor[key]["column"]
                    CUR.execute(query.format(table_name, column, items, name_id, name))
                except KeyError:
                    pass
        num += 1
        if num % 100 == 0:
            CONN.commit()
        return num


def import_canonical_names(yml_file):
    """import the canonical names from a Yml file"""
    with open(yml_file) as ymfp:
        wpcav = yaml.safe_load(ymfp)
    names = wpcav["Names"]

    num = 0
    for name_dict in names:
        if isinstance(name_dict, dict):
            num = sql_importfunctions(name_dict, num)
    CONN.commit()


def import_names_and_context(csv_file):
    """
    reference TEXT,
    line TEXT,
    extracted_name TEXT,
    normalized_name TEXT,
    cluster_key_collision TEXT,
    cluster_levenshtein TEXT,
    cluster_levenshtein_radius2 TEXT,
    cluster_levenshtein_block5 TEXT
    """
    query = """INSERT INTO names_and_context (reference, line, extracted_name,
    normalized_name, cluster_key_collision, cluster_levenshtein,
    cluster_levenshtein_radius2, cluster_levenshtein_block5) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    with open(csv_file) as csvfile:
        name_reader = csv.reader(csvfile, delimiter=",")
        _ = next(name_reader)  # headers
        num = 0
        for row in name_reader:
            CUR.execute(query, tuple(row[1:]))
            num += 1
            if num % 100 == 0:
                CONN.commit()
    CONN.commit()


def related_term_insert(name_id, related_names):
    """Insert each of the related terms on its own line"""
    query = "SELECT name_id FROM canonical_names WHERE canonical_name = ?"
    if isinstance(related_names, list):
        for related in related_names:
            CUR.execute(query, (related,))
            try:
                related_id = CUR.fetchone()[0]
                CUR.execute(
                    """INSERT INTO related_terms
                        (name_id, related_id, related_item)
                        VALUES (?, ?, ?)""",
                    (name_id, related_id, related),
                )
            except TypeError:
                print("List item Error", related)
    else:
        CUR.execute(query, (related_names,))
        try:
            related_id = CUR.fetchone()[0]
            CUR.execute(
                """INSERT INTO related_terms
                        (name_id, related_id, related_item)
                        VALUES (?, ?, ?)""",
                (name_id, related_id, related_names),
            )
        except TypeError:
            print("None_list Error For RT", related_names)


def import_related_and_use(wpacv):
    """Parse the Yaml file for both related and use terms, if they exist,
    populate the database with them"""
    with open(wpacv) as wpfp:
        a_dict = yaml.safe_load(wpfp)
    for name_dict in a_dict["Names"]:
        if isinstance(name_dict, dict):
            for name, items_dict in name_dict.items():
                try:
                    related_names = items_dict["RT"]
                    CUR.execute(
                        "SELECT name_id FROM canonical_names WHERE canonical_name = ?",
                        (name,),
                    )
                    name_id = CUR.fetchone()[0]
                    related_term_insert(name_id, related_names)
                except KeyError:
                    pass
                try:
                    use = items_dict["USE"]
                    CUR.execute(
                        "SELECT name_id FROM canonical_names WHERE canonical_name = ?",
                        (name,),
                    )
                    name_id = CUR.fetchone()[0]
                    if isinstance(use, list):
                        use = use.pop()
                    CUR.execute(
                        "INSERT INTO name_variants (name_id, name_variant) VALUES(?, ?)",
                        (name_id, use),
                    )

                except KeyError:
                    pass
    CONN.commit()


def main():
    """Main function, handles command line arguments"""
    arg_parser = argparse.ArgumentParser(
        description="A script to handle the creation of tables"
    )
    arg_parser.add_argument(
        "-i",
        "--initiate",
        help="Create the tables in the database",
        action="store_true",
    )
    arg_parser.add_argument("-c", "--csv", help="specify a names_and_context csv file")
    arg_parser.add_argument("-y", "--yaml", help="specify a WPACV yaml file to import")
    arg_parser.add_argument(
        "-u",
        "--use",
        help="specify a WPACV yaml file to fill in use and related terms."
        + "Must be run after the database is built",
    )

    args = arg_parser.parse_args()

    if args.initiate:
        table_creator()
    if args.csv:
        import_names_and_context(args.csv)
    if args.yaml:
        import_canonical_names(args.yaml)
    if args.use:
        import_related_and_use(args.use)


if __name__ == "__main__":
    import argparse

    main()
