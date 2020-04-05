#!/usr/bin/env python3 

import sqlite3 

CONN = sqlite3.connect('../data/amarna_name.db')
CUR = CON.cursor()


def main():
    
    # nids 
    CUR.execute('SELECT distinct(name_id) FROM names_and_context WHERE name_id not in (null, '', 0)')
    nids = [x[0] for x in CUR.fetchall()]

    for name_id in nids:







if __name__ == '__main__':
    main()
