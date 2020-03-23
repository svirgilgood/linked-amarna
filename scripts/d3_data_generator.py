#!/usr/bin/env python3

import sqlite3
import json

CONN = sqlite3.Connection("../data/amarna_name.db")
CUR = CONN.cursor()


def return_name_nodes():
    query = """
    SELECT name_id, canonical_name, scope_note
    FROM canonical_names
    WHERE name_id in (
        SELECT distinct(name_id) 
        FROM names_and_context)
    """
    CUR.execute(query)
    results = CUR.fetchall()
    return [
        dict(zip(("name_id", "canonical_name", "scope_note"), res)) for res in results
    ]


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
        print(new_link)
        link_list.append(new_link)

    return link_list


def main():
    """Take the names of the database and show connections between them"""
    nodes = return_name_nodes()
    links = return_name_links()
    node_link_dict = {"nodes": nodes, "links": links}
    with open("../site/graph.json", "w") as jsonfp:
        json.dump(node_link_dict, jsonfp, ensure_ascii=False, indent="  ")


if __name__ == "__main__":
    main()
