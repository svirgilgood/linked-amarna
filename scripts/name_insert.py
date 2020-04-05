#!/usr/bin/env python3

import sqlite3
import re

import name_greper as ng
import interface_functions

CONN = sqlite3.connect("../data/amarna_name.db")
CUR = CONN.cursor()


def id_references(names_list, reference_list):
    try:
        init_ref = reference_list[0]
    except IndexError:
        init_ref = None
    query = """
    SELECT reference, cleaned_text
    FROM ea_texts et 
    WHERE et.reference not in ("""
    query += "'{}'".format(init_ref)

    for reference in reference_list[1:]:
        query += f", '{reference}'"

    query += ")"
    names = [re.sub("m\.", "", name.strip()) for name in names_list]

    query += '\n AND ( et.cleaned_text LIKE "%{}%"'.format(names[0])

    for name in names[1:]:
        # name = name.strip()
        # name = re.sub("m\.", "", name)
        query += f'\n    OR et.cleaned_text LIKE "%{name}%"'
    query += ")"
    return query


def find_names_and_references(name_id):
    query = """
    SELECT reference, normalized_name
    FROM names_and_context
    WHERE name_id = ?"""
    CUR.execute(query, (name_id,))
    reference_list = []
    normalized_name = []
    for reference, name in CUR.fetchall():
        reference_list.append(reference)
        normalized_name.append(name)
    return reference_list, normalized_name


def name_highlighter(ea_text_matches, normalized_names):
    names = [name.replace(" m.", "") for name in normalized_names]
    name_re = ng.rgroup(*names)
    name_pattern = re.compile(name_re, re.IGNORECASE)
    pretty_matches = []
    for text in ea_text_matches:
        search = name_pattern.search(text[1])
        start, end = search.span()
        match = ",".join(search.groups())
        pretty = (
            text[1][:start]
            + "\033[95m"
            + text[1][start:end]
            + "\033[0m"
            + text[1][end:]
        )
        pretty_matches.append([text[0], pretty, match])
    return pretty_matches


def insert_new_matches(reference, normalized_name, name_id):
    iquery = """
    INSERT INTO names_and_context (reference, line, normalized_name, name_id)
    VALUES (?, (SELECT line FROM ea_texts WHERE reference = ? LIMIT 1), ?, ?)"""
    CUR.execute(iquery, (reference, reference, normalized_name, name_id))


def input_manager(pretty_matches, name_id):
    """Input manager for row matches"""
    CUR.execute(
        "SELECT name_id, canonical_name, scope_note FROM canonical_names WHERE name_id = ?",
        (name_id,),
    )
    print(CUR.fetchone())
    headings = ["index", "reference", "line", "match"]
    interface_functions.nice_rows(pretty_matches, headings=headings)
    index = input(
        "Which references match the name_id? index numbers (in comma seperated form), all, none\n"
    )

    if index == "all":
        index = [x for x in range(len(pretty_matches))]
    elif index == "none":
        index = []
    else:
        index = [int(i) for i in index.split(",")]
    for i in index:
        reference = pretty_matches[i][0]
        normalized_name = pretty_matches[i][-1]
        insert_new_matches(reference, normalized_name, name_id)
    CONN.commit()


def insert_hess_number(name_id, hess_id):
    iquery = "UPDATE canonical_names SET hess = ? WHERE name_id = ?"
    CUR.execute(iquery, (hess_id, name_id))
    CONN.commit()


def main():
    aparser = argparse.ArgumentParser()
    aparser.add_argument("name_id", nargs="+", help="name ids to look for")
    aparser.add_argument(
        "-n", "--normalized", help="list of comma seperated normalized names"
    )
    aparser.add_argument(
        "-a",
        "--apn",
        help="add number from R. Hesses _Amarna Personal Names_ to canonical_name table",
    )

    args = aparser.parse_args()

    for nid in args.name_id:
        reference_list, normalized_name = find_names_and_references(nid)
        if args.normalized:
            normalized_name = args.normalized.split(",")
        if args.apn:
            insert_hess_number(nid, args.apn)
            continue

        query = id_references(normalized_name, reference_list)
        CUR.execute(query)  # , reference_list)
        ea_text_matches = CUR.fetchall()
        pretty_matches = name_highlighter(ea_text_matches, normalized_name)
        input_manager(pretty_matches, nid)


if __name__ == "__main__":
    import argparse

    main()
