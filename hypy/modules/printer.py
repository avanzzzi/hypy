"""
Printer module. Formats messages to be printed in command line.
"""
from datetime import timedelta
from modules.snaptree import create_tree
from fnmatch import fnmatch

STATES = {3: 'off',
          2: 'running',
          9: 'paused',
          6: 'saved'}


def print_vm_snaps(snaps_json: dict, vm_name: str):
    """
    Print ascii tree of checkpoints.

    Args:
        snaps_json: Dict containing the table of checkpoints.
        vm_name: Vm name to be shown as root of the tree.
    """
    t_snaps = create_tree(snaps_json,
                          vm_name,
                          f_pid="ParentSnapshotId",
                          f_id="Id",
                          f_label="Name",
                          f_ctime="CreationTime",
                          v_none=None,
                          colors=True)
    print("-- Virtual Machine Snapshots --")
    print(t_snaps)


def print_list_vms(vms_json: dict, filter_vms: str):
    """
    Print list of virtual machines.

    Args:
        vms_json: Dict containing the table of vms.
        filter_vms: Filter to be applied at the output. Only the vms whose name
            matches the filter will be shown.
    """
    # Listing
    # print("-- Hyper-V Virtual Machine Listing --")

    # Header
    print("{} {} {} {}".format("Index".rjust(5),
                               "State".ljust(7),
                               "Name".ljust(30),
                               "Uptime"))

    if filter_vms:
        vms_show = [vm for vm in vms_json if fnmatch(vm['Name'], filter_vms)]
    else:
        vms_show = vms_json

    # Listing
    for vm in vms_show:
        index = str(vms_json.index(vm)).rjust(3)
        state = STATES.get(vm['State'], "unknown").ljust(7)
        name = str(vm['Name']).ljust(30)
        uptime = str(timedelta(hours=vm['Uptime']['TotalHours']))
        print("[{}] {} {} {}".format(index, state, name, uptime))
