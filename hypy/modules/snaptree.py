"""
Snaptree module. Groups the functions used to create the tree of checkpoints.
"""
import re
from collections import OrderedDict as OD
from datetime import datetime

from asciitree import LeftAligned


def convert_dt(creation_time: str) -> str:
    """
    Convert hyper-v timestamp to readable datetime.

    Args:
        creation_time: Timestamp with the snapshot creation date.
    Returns:
        Datetime string in readable format.
    """
    c = datetime.fromtimestamp(float(re.search("[0-9]+",
                                     creation_time).group())/1000.0)
    return c.strftime("%d/%m/%Y %H:%M:%S")


def create_tree(table: dict,
                root: str,
                mark: str,
                f_pid: str = "pid",
                f_id: str = "id",
                f_label: str = "item",
                f_ctime: str = "ctime",
                v_none: str = "null") -> str:
    """
    Creates the ascii checkpoint tree.

    Args:
        table: List of checkpoints as a table.
        root: Root label of the tree.
        mark: Current snapshot name. Mark the element with an '*'
        f_pid: Field of the table that contains the parent id of the node.
        f_id: Field of the table that contains the id of the node.
        f_label: Field with the label of the node.
        f_ctime: Field with the timestamp creation date.
        v_none: Value to be used for empty fields.
    Returns:
        A string containing the tree of snapshots
    """
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

    for cell in table:
        if cell[f_label] == mark:
            cell[f_label] = "{}*".format(cell[f_label])

        tr_tree = tr_tree.replace(cell[f_id],
                                  "{} ({})".format(
                                      cell[f_label],
                                      convert_dt(cell[f_ctime])))
    return tr_tree


def walk(node: dict, search_key: str, insert_key: str) -> str:
    """
    Walk in the tree to find where to insert the element.

    Args:
        node: The tree so far.
        search_key: Where to insert the new value.
        insert_key: The element to be inserted.
    Yields:
        List of inserted items in the current iteration.
    """
    for k, v in node.items():
        if k == search_key:
            if insert_key not in node[k].keys():
                node[k][insert_key] = OD()
                yield insert_key
        elif isinstance(v, OD):
            yield from walk(v, search_key, insert_key)
