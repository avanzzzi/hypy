#!/usr/bin/env python3
# coding: utf-8
from winrm import Protocol
from winrm import Response
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
import subprocess
import json
import os.path
import time
import platform
import re

vms = None
server = None
config = None
vms_cache_filename = None
states = {3: 'off',
          2: 'running',
          9: 'paused',
          6: 'saved'}


def connect(index):
    """
    Connect to virtual machine by index using freerdp

    Args:
        index (int): The machine's index generated in the current cache
    """
    load_vms()

    vm_id = vms[index]['Id']
    user = config['user']
    passw = config['pass']
    host = config['host']

    vm_info = get_vm(index)
    if vm_info != '' and vm_info['State'] != 2 and vm_info['State'] != 9:
        start_vm(index)
        time.sleep(2)

    if platform.uname()[0] == "Linux":
        freerdp_bin = "xfreerdp"
    elif platform.uname()[0] == "Windows":
        freerdp_bin = "wfreerdp.exe"

    cmd = [freerdp_bin, '/v:{0}'.format(host), '/vmconnect:{0}'.format(vm_id), '/u:{0}'.format(user),
           '/p:{0}'.format(passw),
           '/t:{} [{}] {}'.format(host, index, vm_info['Name']), '/cert-ignore']

    # print(cmd)
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        #subprocess.Popen(cmd)
    except FileNotFoundError:
        print("{} not found in PATH".format(freerdp_bin))
    # retval = p.wait()


def update_cache(index, new_state):
    """
    Update machine state on cache by index
    Called after start, stop, pause and resume operations

    Args:
        index (int): machine index in current cache
        new_state (int): represented by states dict
    """
    if vms != None:
        vms[index]['State'] = new_state

        with open(vms_cache_filename, 'w') as vms_cache_file:
            json.dump(vms, vms_cache_file, indent=4)


def update_all_cache(force=False):
    """
    Checks cache file modification time and update vm list
    Creates cache file if nonexistent

    Args:
        force (bool, optional): Whether should force cache update or not

    Returns:
        bool: True for success
    """
    #if use_cache_file:
    modified = datetime.min
    if os.path.isfile(vms_cache_filename):
        modified = datetime.fromtimestamp(os.path.getmtime(vms_cache_filename))

    if modified < datetime.now() - timedelta(hours=int(config['sync_interval'])) or force:

        vms_json = fetch_data()
        if vms_json != "":
            with open(vms_cache_filename, 'w') as vms_cache_file:
                json.dump(vms_json, vms_cache_file, indent=4)
        else:
            return False

    return True

def fetch_data():
    """
        Fetch vm data from hyper-v server
        Creates cache file if nonexistent

        Returns:
            dict: json dict contaning hyper-v data
        """
    print ("Fetching new data...")
    ps_script = "Get-VM * | Select Name,Id,State,Uptime | ConvertTo-Json"
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return ""

    vms_json = json.loads(rs.std_out.decode('latin-1'))

    # If there is only one vm, make it a list
    if type(vms_json) is dict:
        vms_json = [vms_json]

    return vms_json


def load_vms(no_cache=False):
    """
    Loads current cache file into memory

    Returns:
        bool: True for success
    """
    global vms

    try:
        if not no_cache:
            with open(vms_cache_filename, 'r') as vms_cache_file:
                vms = json.load(vms_cache_file)
        else:
            vms = fetch_data()
    except IOError:
        print("Cannot access file {0}".format(vms_cache_filename))
        return False
    except ValueError:
        print ("JSONDecodeError, cannot decode cache file {0}".format(vms_cache_filename))
        return False
    except Exception:
        print ("Error load_vms()")
        return False

    return True


def list_vms():
    """
    List virtual machines
    """
    load_vms()

    # Listing
    print("-- Hyper-V Virtual Machine Listing --")

    # Header
    print("{0} {1} {2} {3}".format("Index".rjust(5), "State".ljust(7), "Name".ljust(30), "Uptime"))

    # Listing
    for vm in vms:
        index = str(vms.index(vm)).rjust(3)
        state = states.get(vm['State'], "unknown").ljust(7)
        name = str(vm['Name']).ljust(30)
        uptime = str(timedelta(hours=vm['Uptime']['TotalHours']))
        print("[{0}] {1} {2} {3}".format(index, state, name, uptime))


def load_switches():
    """
        Fetch switches information from hyper-v server
        Returns:
            dict: json dict contaning switches hyper-v data
        """
    print ("Fetching switches data...")
    ps_script = "Get-VMSwitch * | Select Name | ConvertTo-Json"
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return ""

    switches_json = json.loads(rs.std_out.decode('latin-1'))

    # If there is only one vm, make it a list
    if type(switches_json) is dict:
        switches_json = [switches_json]

    print("-- Virtual Network Switches --")
    print("{0}".format("Name".ljust(30)))
    for switch in switches_json:
        name = str(switch['Name']).ljust(30)
        print("{0}".format(name))

    return switches_json


def set_vm_switch(vm_index, switch, vm_name=""):
    """
        Change vm switch based on its name

        Args:
            vm_index (int): The machine's index generated in the current cache (optional)
            switch (str): switch name to be changed
            vm_name (str): vm name that will be changed its switch

        Returns:
            True - Changed successfully
            False - Change has failed
        """
    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Connect-VMNetworkAdapter -VMName {0} -SwitchName {1}".format(vm_name, switch)
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    return True


def get_vm_network(vm_index, vm_name=""):
    """
        Get network configuration from vm

        Args:
            vm_index (int): The machine's index generated in the current cache (optional)
            vm_name (str): vm name that will be changed its switch

        Returns:
            json object containing fetched data
        """
    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    print ("index: {} name:{}".format(vm_index, vm_name))

    ps_script = "Get-VM -VMName {0} | Select -ExpandProperty networkadapters | Select Name,SwitchName,MacAddress,IPAddresses,Status | ConvertTo-Json".format(
        vm_name)

    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    try:
        na_json = json.loads(rs.std_out.decode('latin-1'))
    except Exception as e:
        print("Virtual Machine {} has problem with network adapters: {}".format(vm_name, e))
        return

    # If there is only one network adapter, make it a list
    if type(na_json) is dict:
        na_json = [na_json]

    print("-- Virtual Machine Network Adapter --")
    print("{0} {1} {2} {3} {4}".format("Name".ljust(20), "SwitchName".ljust(20), "MacAddress".ljust(20), "Status".ljust(10), "IPAddresses"))
    for na in na_json:
        snapname = str(na['Name']).ljust(20)
        switchname = str(na['SwitchName']).ljust(20)
        mac = str(na["MacAddress"]).ljust(20)
        status = str(na["Status"]).ljust(10)
        ip = str(na["IPAddresses"])
        print("{0} {1} {2} {3} {4}".format(snapname, switchname, mac, status, ip))

    return na_json


def list_vm_snaps(vm_index, vm_name=""):
    """
    List vm snapshots by vm index

    Args:
        vm_index (int): The machine's index generated in the current cache
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Get-VMSnapshot -VMName {0} | Select Name,ParentSnapshotName,CreationTime | ConvertTo-Json".format(vm_name)

    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    try:
        snaps_json = json.loads(rs.std_out.decode('latin-1'))
    except Exception as e:
        print("Virtual Machine {} has no snapshots: {}".format(vm_name, e))
        return

    # If there is only one snap, make it a list
    if type(snaps_json) is dict:
        snaps_json = [ snaps_json ]

    print("-- Virtual Machine Snapshots --")
    print("{0} {1} {2}".format("Name".ljust(30), "Parent".ljust(30), "CreationTime"))
    for snap in snaps_json:
        snapname = str(snap['Name']).ljust(30)
        parent = str(snap['ParentSnapshotName']).ljust(30)
        creation = datetime.fromtimestamp(float(re.search("[0-9]+", snap['CreationTime']).group())/1000.0)
        print("{0} {1} {2}".format(snapname, parent, creation.strftime("%d/%m/%Y %H:%M:%S")))


def restore_vm_snap(vm_index, snap_name, force=False, vm_name="", no_cache=False):
    """
    Restore virtual machine snapshot

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be restored

    Returns:
        bool: True if success
    """

    if vm_name == "" and vm_index != -1:
        load_vms(no_cache)
        vm_name = vms[vm_index]['Name']

    if force:
        vm = get_vm(-1, vm_name)
        state = states.get(vm['State'], "unknown")
        print ("Vm in '{}' state".format(state))
        if "off" in state or "saved" in state:
            start_vm(-1, vm_name)

    ps_script = 'Restore-VMSnapshot -Name "{0}" -VMName {1} -Confirm:$false'.format(snap_name, vm_name)

    print('Restoring snapshot "{0}" in {1}'.format(snap_name, vm_name))
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def remove_vm_snapshot(vm_index, snap_name, recursive=False, vm_name=""):
    """
    Deletes a virtual machine checkpoint

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be deleted
        recursive (bool, optional): Specifies that the checkpoint’s children are to be
            deleted along with the checkpoint

    Returns:
        bool: True if success
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = 'Remove-VMSnapshot -VMName "{0}" -Name "{1}"'.format(vm_name, snap_name)
    if recursive:
        ps_script += " -IncludeAllChildSnapshots"
    ps_script += " -Confirm:$false"

    print('Removing snapshot "{0}" in "{1}"'.format(snap_name, vm_name))
    if recursive:
        print("and it's children")
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def create_vm_snapshot(vm_index, snap_name, vm_name=""):
    """
    Create a new snapshot with vm's current state

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be created

    Returns:
        bool: True if success
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = 'Checkpoint-VM -Name "{0}" -SnapshotName "{1}" -Confirm:$false'.format(vm_name, snap_name)

    print('Creating snapshot "{0}" in "{1}"'.format(snap_name, vm_name))
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def get_vm(vm_index, vm_name=""):
    """
    Gets vm info by index

    Args:
        vm_index (int): The machine's index generated in the current cache
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Get-VM -Name {0} | Select Name,Id,State | ConvertTo-Json".format(vm_name)
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return

    vm_json = json.loads(rs.std_out.decode('latin-1'))
    return vm_json


def stop_vm(vm_index, force=False, vm_name=""):
    """
    Stop virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
        force (bool): Whether should force shutdown or not
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Stop-VM -Name {}".format(vm_name)
    if force:
        ps_script += " -Force"

    print('Stopping VM "{}", force: {}'.format(vm_name, force))
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 3)
    print("Success")
    return True


def resume_vm(vm_index, vm_name=""):
    """
    Resume (paused) virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Resume-VM -Name {0}".format(vm_name)

    print('Resuming VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 2)
    print("Success")
    return True


def pause_vm(vm_index, vm_name=""):
    """
    Pause virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Suspend-VM -Name {0}".format(vm_name)

    print('Pausing VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 9)
    print("Success")
    return True


def start_vm(vm_index, vm_name=""):
    """
    Start virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """

    if vm_name == "" and vm_index != -1:
        load_vms()
        vm_name = vms[vm_index]['Name']

    ps_script = "Start-VM -Name {0}".format(vm_name)

    print('Starting VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 2)
    print("Success")
    return True


def validate_vm_index(vm_index, vm_name):
    if vm_name == "" and vm_index > 0:
        load_vms()
        return vms[vm_index]['Name']
    elif vm_name != "" and vm_index == -1:
        return vm_name
    else:
        raise Exception("Vm name '{}' is invalid!".format(vm_name))


def setup(configp):
    """
    Setup hvclient globals and create protocol with server host and credentials

    Args:
        configp (dict): Configuration from config file
    """
    global config
    global server
    global vms_cache_filename

    config = configp

    domain = config['domain']
    user = config['user']
    passw = config['pass']
    host = config['host']
    vms_cache_filename = config['cache_file']

    server = Protocol(endpoint='http://{0}:5985/wsman'.format(host),
                      transport='ntlm',
                      username='{0}\{1}'.format(domain, user),
                      password=passw,
                      server_cert_validation='ignore')


def run_ps(ps, proto):
    """
    Run powershell script on target machine

    Args:
        ps (str): Powershell script to run
        proto (Protocol): Protocol containing target machine

    Returns:
        Response: Object containing stderr, stdout and exit_status
    """
    encoded_ps = b64encode(ps.encode('utf_16_le')).decode('ascii')
    rs = run_cmd('powershell -encodedcommand {0}'.format(encoded_ps), proto)
    return rs


def run_cmd(cmd, proto):
    """
    Run batch script on target machine

    Args:
        cmd (str): batch script to run
        proto (Protocol): Protocol containing target machine

    Returns:
        Response: Object containing stderr, stdout and exit_status
    """
    shell_id = proto.open_shell()
    command_id = proto.run_command(shell_id, cmd)
    rs = Response(proto.get_command_output(shell_id, command_id))
    proto.cleanup_command(shell_id, command_id)
    proto.close_shell(shell_id)
    return rs
