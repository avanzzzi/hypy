from os.path import isfile, getmtime
from datetime import datetime, timedelta
import json

vms_cache_filename = None


def list_vms():
    if isfile(vms_cache_filename):
        with open(vms_cache_filename, 'r') as vms_cache_file:
            vms_cache = json.load(vms_cache_file)

        return vms_cache


def update_cache(vms_json):
    # If there is only one vm, make it a list
    if isinstance(vms_json, dict):
        vms_json = [vms_json]

    if isfile(vms_cache_filename):
        with open(vms_cache_filename, 'r') as vms_cache_file:
            vms_cache = json.load(vms_cache_file)

        vms_json = list({x['Id']: x for x in vms_cache + vms_json}.values())

    vms_json.sort(key=lambda k: k['Name'])
    with open(vms_cache_filename, 'w') as vms_cache_file:
        json.dump(vms_json, vms_cache_file, indent=4)


def need_update(force=False):
    modified = datetime.min
    if isfile(vms_cache_filename):
        modified = datetime.fromtimestamp(getmtime(vms_cache_filename))

    if modified < datetime.now() - timedelta(hours=int(config['sync_interval'])) or force:
        return True

    return False


def update_all_cache(force=False):
    """
    Checks cache file modification time and update vm list
    Creates cache file if nonexistent

    Args:
        force (bool, optional): Whether should force cache update or not

    Returns:
        bool: True for success
    """
    modified = datetime.min
    if isfile(vms_cache_filename):
        modified = datetime.fromtimestamp(getmtime(vms_cache_filename))

    if modified < datetime.now() - timedelta(hours=int(config['sync_interval'])) or force:
        ps_script = "Get-VM * | Select Name,Id,State,Uptime | sort Name | ConvertTo-Json"
        rs = run_ps(ps_script)

        if rs.status_code != 0:
            print(rs.std_err)
            return False

        vms_json = json.loads(rs.std_out.decode('latin-1'))
        update_cache(vms_json)

    return True


def load_vms_from_cache():
    """
    Loads current cache file into memory

    Returns:
        bool: True for success
    """
    vms = None
    try:
        with open(vms_cache_filename, 'r') as vms_cache_file:
            vms = json.load(vms_cache_file)
    except IOError:
        print("Cannot access file {0}".format(vms_cache_filename))

    return vms
