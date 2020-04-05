#!/usr/bin/env python3

import sqlite3
import json
import re
import unicodedata

CONN = sqlite3.Connection("../data/amarna_name.db")
CUR = CONN.cursor()


def remove_diacritics(string):
    for c in unicodedata.normalize("NFD", string):
        if unicodedata.category(c)[0] != "M":
            yield c


def return_name_nodes():
    query = """
    SELECT cn.name_id, cn.canonical_name, cn.language, cn.scope_note, 
        (SELECT count(nac.reference) 
        FROM names_and_context nac 
        WHERE nac.name_id = cn.name_id) as hits
    FROM canonical_names cn
    WHERE cn.name_id in (
        SELECT distinct(name_id) 
        FROM names_and_context)
    """
    CUR.execute(query)
    results = CUR.fetchall()
    return [
        dict(zip(("name_id", "canonical_name", "language", "scope_note", "hits"), res))
        for res in results
    ]


def language_parser(nodes):
    update_node_language = []
    language_set = set()
    for node in nodes:
        language = node["language"]
        if language:
            l_match = re.match(r"[\w\-]+", language)
            language = l_match.group()
            language_set.add(language)
            node["language"] = language
        if not language:
            node["language"] = "Unknown"
        update_node_language.append(node)

    for lang in language_set:
        print(lang)
    return update_node_language


def return_name_links():
    query = """
    SELECT reference, name_id
    FROM names_and_context
    WHERE name_id is not null
    AND name_id != 0
    """
    CUR.execute(query)
    results = CUR.fetchall()
    link_dict = {}

    for res in results:
        ref, _ = res[0].split(":")
        link_dict.setdefault(ref, set()).add(res[1])

    links = set()
    for name_set in link_dict.values():
        for name_id in name_set:
            if name_id != "":
                for other_id in name_set:
                    if other_id not in (name_id, ""):
                        links.add(frozenset({other_id, name_id}))

    link_list = []
    for link in links:
        new_link = dict(zip(["source", "target"], link))
        link_list.append(new_link)

    return link_list


def return_references(nodes):
    query = """
    SELECT nac.reference, nac.name_id 
    FROM names_and_context nac
    JOIN canonical_names cn 
      ON cn.name_id = nac.name_id
    """
    CUR.execute(query)
    ref_list = CUR.fetchall()
    ref_dict = {}
    for ref in ref_list:
        ref_dict.setdefault(ref[1], []).append(ref[0])

    for node in nodes:
        node["occurances"] = ref_dict[node["name_id"]]

    return nodes


def return_variant_spellings(nodes):
    query = """
    SELECT nac.normalized_name, nac.name_id
    FROM names_and_context nac
    WHERE  nac.name_id in (SELECT cn.name_id FROM canonical_names cn );
    """
    CUR.execute(query)
    results = CUR.fetchall()
    name_variants = {}

    for res in results:
        normalized_name = res[0].replace(" m.", "").replace("m.", "")
        romanized_name = "".join(remove_diacritics(normalized_name))
        name_variants.setdefault(res[-1], []).append(normalized_name)
        name_variants[res[-1]].append(romanized_name)

    unique_variants = {
        key: [x for x in set(value) if x not in ("", "_")]
        for key, value in name_variants.items()
    }

    for node in nodes:
        node["variants"] = unique_variants[node["name_id"]]

    return nodes


def variant_parser(nodes):
    variants = []
    for node in nodes:
        variants.append(
            {
                "canonical_name": node["canonical_name"],
                "variant": node["canonical_name"],
                "name_id": node["name_id"],
            }
        )
        for var in node["variants"]:
            variants.append(
                {
                    "canonical_name": node["canonical_name"],
                    "variant": var,
                    "name_id": node["name_id"],
                }
            )
    return variants


def main():
    """Take the names of the database and show connections between them"""
    nodes = return_name_nodes()
    nodes = language_parser(nodes)
    nodes = return_variant_spellings(nodes)
    nodes = return_references(nodes)
    links = return_name_links()
    variants = variant_parser(nodes)
    node_link_dict = {"nodes": nodes, "links": links, "variants": variants}
    with open("../site/graph3.json", "w") as jsonfp:
        json.dump(node_link_dict, jsonfp, ensure_ascii=False, indent="  ")


if __name__ == "__main__":
    main()
