#!/usr/bin/env python3

import yaml
import pandas as pd
import sqlite3
import json

from fuzzywuzzy import fuzz

CONNECTION = sqlite3.connect("amarna_name.db")
CUR = CONNECTION.cursor()


def nice_rows(rows, headings=False, index_start=0, pad=3):
    """Printing nice rows to make reading easier
    """
    col_widths = [3]
    for i in range(len(rows[0])):
        col_widths.append(max(len(str(row[i])) for row in rows))

    if headings:
        for i, heading in enumerate(headings):
            print(
                "\033[95m{1:{0}}".format(col_widths[i] + pad, str(heading)),
                end="\033[0m",
            )
        print()

    for index, row in enumerate(rows):
        row = [index + index_start] + list(row)
        for i, field in enumerate(row):
            print("{1:{0}}".format(col_widths[i] + pad, str(field)), end="")
        print()


def input_manager(tname, potential_matches, index_start=0, canonical_names=False):
    """Handle the input functions to approve matches based on levenshtein distances"""
    total_matches = len(potential_matches)
    print(f"\nWhich example matches {tname[2]} (total matches: {total_matches})?")
    print(f"Example reference: {tname[0]}")
    """
    for index, pmatch in enumerate(potential_matches[index_start : index_start + 10]):
        ratio, form, can_form = pmatch
        index = index + index_start
        print(f"{index}.\t {ratio} \t {form} \t {can_form}")
    """

    headings = ["index", "Lev", "id", "variant", "canonical", "scope_note"]
    nice_rows(
        potential_matches[index_start : index_start + 10],
        headings=headings,
        index_start=index_start,
    )
    index = input(
        "Type the index number or type next to see more. If no matches add one to total number\n"
    )
    index = index.strip()
    try:
        index = int(index)
        if index > (index_start + 9):
            match = None
        else:
            try:
                match = potential_matches[index]
            except IndexError:
                match = None

    except ValueError:
        if index == "next":
            index_start += 10
            match = input_manager(tname, potential_matches, index_start=index_start)
        elif index == "id":
            name_id = input("What ID number matches this name?\n")
            name_id = int(name_id)
            if name_id == 0:
                match = (0, "", "", "")
            elif canonical_names:
                match = [
                    cname for cname in canonical_names if cname[0] == name_id
                ].pop()
                match = (" ", *match)
            else:
                match = None
        else:
            match = None
    return match


def link_text_to_canonical_name(name_id, text_name):
    insert_query = """
    UPDATE names_and_context
    SET name_id = ?
    WHERE cluster_levenshtein_block5 = ?
    """
    CUR.execute(insert_query, (name_id, text_name))
    CONNECTION.commit()


def fuzzy_match_names(text_names, canonical_names):
    """fuzzy matching for potential
    text names ('reference', 'normalized_name', 'levensthtein_cluster')
    canonical_names ('name_id', 'name_variant', 'canonical_name', 'scope_note')
    """
    matched_names = []
    for text_name in text_names:
        tname = text_name[-1].replace(" m.", "")
        potential_matches = []
        for cname in canonical_names:
            ratio = fuzz.ratio(tname, cname[1])
            if ratio > 25:
                potential_matches.append((ratio, *cname))
        potential_matches = sorted(potential_matches, key=lambda x: x[0], reverse=True)
        try:
            pot_match = input_manager(
                text_name, potential_matches, canonical_names=canonical_names
            )
        except IndexError:
            continue
        if pot_match:
            print(pot_match, "\n")
            name_id = pot_match[1]
            link_text_to_canonical_name(name_id, text_name[2])
            matched_names.append([tname, *pot_match])
    return matched_names


def grab_names_to_compare():
    """Retruns names and variants for using fuzzy matching on"""
    variant_query = """
    SELECT nv.name_id, nv.name_variant, nc.canonical_name, nc.scope_note
    FROM name_variants nv
    JOIN canonical_names nc
      ON nc.name_id = nv.name_id
    """
    CUR.execute(variant_query)
    variants = CUR.fetchall()
    text_query = """
    SELECT reference, normalized_name, cluster_levenshtein_block5
    FROM names_and_context
    WHERE name_id is null
    GROUP BY cluster_levenshtein_block5
    """
    CUR.execute(text_query)
    text_variants = CUR.fetchall()
    return variants, text_variants


def main():
    """
    with open("WPACV.yml") as fp:
        wpacv = yaml.safe_load(fp)
    dataframe = pd.read_csv("AmarnaNamesCleaned.csv")
    list_of_names = list(dataframe["cluster_levenshtein_block5"].unique())
    """

    can_variants, text_variants = grab_names_to_compare()
    matched_names = fuzzy_match_names(text_variants, can_variants)
    with open("matches.json") as fp:
        json.dump(fp, matched_names)


if __name__ == "__main__":
    main()
