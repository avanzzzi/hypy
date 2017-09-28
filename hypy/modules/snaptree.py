import re
from asciitree import LeftAligned
from collections import OrderedDict as OD
from datetime import datetime
from colorama import Fore


def convert_dt(creation_time):
    c = datetime.fromtimestamp(float(re.search("[0-9]+",
                                     creation_time).group())/1000.0)
    return c.strftime("%d/%m/%Y %H:%M:%S")


def create_tree(table,
                root,
                f_pid="pid",
                f_id="id",
                f_label="item",
                f_ctime="ctime",
                v_none="null",
                colors=False):
    items = [(c[f_pid], c[f_id]) for c in table]
    tree = {root: OD()}
    inserted = []

    while [x[1] for x in items if x[1] not in inserted]:
        for parent, item in items:
            if parent == v_none:
                parent = root
            inserts = walk(tree, parent, item)
            inserted.extend(list(inserts))

    tr = LeftAligned()
    tr_tree = tr(tree)

    if not colors:
        for cell in table:
            tr_tree = tr_tree.replace(cell[f_id],
                                      "{} ({})".format(cell[f_label], convert_dt(cell[f_ctime])))
    else:
        for cell in table:
            tr_tree = tr_tree.replace(cell[f_id],
                                      "{}{} {}({}){}".format(Fore.LIGHTWHITE_EX, cell[f_label], Fore.CYAN, convert_dt(cell[f_ctime]), Fore.RESET))

    return tr_tree


def walk(node, search_key, insert_key):
    for k, v in node.items():
        if k == search_key:
            if insert_key not in node[k].keys():
                node[k][insert_key] = OD()
                yield insert_key
        elif isinstance(v, OD):
            yield from walk(v, search_key, insert_key)
