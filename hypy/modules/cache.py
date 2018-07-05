"""
Cache module. Interacts with the cache file.
"""
from datetime import datetime, timedelta
from json import JSONDecodeError, dump, load
from os import remove
from os.path import getmtime, isfile, join
from tempfile import gettempdir

sync_interval = None
current_host = None


def get_cache_path() -> str:
    """
    Get the cache file path based on the current Hyper-V host.

    Returns:
        The path to be used to create or update de cache file.
    """
    vms_cache = join(gettempdir(), 'vms_{}.cache'.format(current_host))
    return vms_cache


def get_vm_by_name(name: str) -> dict:
    """
    Get vm from cache.

    Args:
        name: The name of the virtual machine.
    Returns:
        The vm info found in the cache.
    """
    vms = list_vms()
    vm = [vm for vm in vms if vm['Name'] == name][0]
    vm['index'] = vms.index(vm)
    return vm


def get_vm_by_index(index: str) -> dict:
    """
    Get vm from cache.

    Args:
        index: The index of the vm in the cache.
    Returns:
        The vm info found in the cache.
    """
    vms = list_vms()
    vm = vms[int(index)]
    vm['index'] = index
    return vm


def list_vms() -> list:
    """
    Get all vms from cache.

    Returns:
        All vm info found in cache.
    """
    vms_cache_filename = get_cache_path()
    try:
        with open(vms_cache_filename, 'r') as vms_cache_file:
            vms_cache = load(vms_cache_file)
    except FileNotFoundError:
        print("Cache file not found")
        vms_cache = []
    except JSONDecodeError:
        print("Invalid cache file")
        vms_cache = []

    return vms_cache


def update_cache(vms_json: dict):
    """
    Update current cache with new information.

    Args:
        vms_json: Information to be included in cache.
    """
    # If there is only one element, make it a list
    if isinstance(vms_json, dict):
        vms_json = [vms_json]

    vms_cache_filename = get_cache_path()
    if isfile(vms_cache_filename):
        vms_cache = list_vms()
        vms_json = list({x['Id']: x for x in vms_cache + vms_json}.values())

    vms_json.sort(key=lambda k: k['Name'])
    with open(vms_cache_filename, 'w') as vms_cache_file:
        dump(vms_json, vms_cache_file, indent=4)


def need_update() -> bool:
    """
    Cheks if cache needs update based on cache file modification date.

    Returns:
        True if the cache file is older than sync interval in hours.
    """
    vms_cache_filename = get_cache_path()
    modified = datetime.min
    if isfile(vms_cache_filename):
        modified = datetime.fromtimestamp(getmtime(vms_cache_filename))

    if modified < datetime.now() - timedelta(hours=int(sync_interval)):
        return True

    return False


def remove_cache() -> bool:
    """
    Remove the current host cache file.

    Returns:
        Whether the file was removed with success.
    """
    vms_cache_filename = get_cache_path()
    if isfile(vms_cache_filename):
        remove(vms_cache_filename)

    return not isfile(vms_cache_filename)


def get_name(by_name, ident):
    """Retrieve name or name by index based on user input."""
    if by_name:
        name = ident
    else:
        index = ident
        name = get_vm_by_index(index)['Name']

    return name
