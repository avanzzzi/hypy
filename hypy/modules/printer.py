from colorama import init, Fore
from datetime import timedelta
from modules.snaptree import create_tree
import json


init()
states = {3: 'off',
          2: 'running',
          9: 'paused',
          6: 'saved'}


def parse_result(rs):
    pass


def print_vm_snaps(vm_name, rs):
    """
    """
    if rs.status_code != 0:
        print('{}Error: {}{}'.format(Fore.RED, Fore.RESET, rs.std_err))
        return False

    try:
        snaps_json = json.loads(rs.std_out.decode('latin-1'))
    except Exception as e:
        print("Virtual Machine {} has no snapshots: {}".format(vm_name, e))
        return False

    # If there is only one snap, make it a list
    if isinstance(snaps_json, dict):
        snaps_json = [snaps_json]

    t_snaps = create_tree(snaps_json, vm_name, f_pid="ParentSnapshotId",
                          f_id="Id",
                          f_label="Name",
                          f_ctime="CreationTime",
                          v_none=None,
                          colors=True)
    print("{}-- Virtual Machine Snapshots --".format(Fore.GREEN))
    print('{}{}'.format(Fore.RESET, t_snaps))


def print_list_vms(vms_json):
    """
    """
    # Listing
    print("-- Hyper-V Virtual Machine Listing --")

    # Header
    print("{} {} {} {}".format("Index".rjust(5),
                               "State".ljust(7),
                               "Name".ljust(30),
                               "Uptime"))

    # Listing
    for vm in vms_json:
        index = str(vms_json.index(vm)).rjust(3)
        state = states.get(vm['State'], "unknown").ljust(7)
        name = str(vm['Name']).ljust(30)
        uptime = str(timedelta(hours=vm['Uptime']['TotalHours']))
        print("[{}] {} {} {}".format(index, state, name, uptime))
