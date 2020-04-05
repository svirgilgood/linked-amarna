#!/usr/bin/env python3


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def nice_rows(rows, headings=False, index_start=0, pad=3):
    """Printing nice rows to make reading easier
    """
    col_widths = [3]
    for i in range(len(rows[0])):
        col_widths.append(max(len(str(row[i])) for row in rows))

    if headings:
        for i, heading in enumerate(headings):
            print(
                "{0}{2:{1}}".format(bcolors.HEADER, col_widths[i] + pad, str(heading)),
                end=bcolors.ENDC,
            )
        print()

    for index, row in enumerate(rows):
        row = [index + index_start] + list(row)
        for i, field in enumerate(row):
            print("{1:{0}}".format(col_widths[i] + pad, str(field)), end="")
        print()
