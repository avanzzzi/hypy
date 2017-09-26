#!/usr/bin/env python3
# coding: utf-8

import json
import os.path
import time
import platform
from collections import namedtuple
from paramiko import SSHClient
from subprocess import Popen, DEVNULL
from winrm import Protocol
from winrm import Response
from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from snaptree import create_tree

vms = None
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
        time.sleep(10)

    if platform.uname()[0] == "Windows":
        freerdp_bin = "wfreerdp.exe"
    else:
        freerdp_bin = "xfreerdp"

    cmd = [freerdp_bin, '/v:{0}'.format(host),
                        '/vmconnect:{0}'.format(vm_id),
                        '/u:{0}'.format(user),
                        '/p:{0}'.format(passw),
                        '/t:{} [{}] {}'.format(host, index, vm_info['Name']),
                        '/cert-ignore']

    try:
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as err:
        print("{} not found in PATH\n{}".format(freerdp_bin, err))


def update_cache(index, new_state):
    """
    Update machine state on cache by index
    Called after start, stop, pause and resume operations

    Args:
        index (int): machine index in current cache
        new_state (int): represented by states dict
    """
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
    modified = datetime.min
    if os.path.isfile(vms_cache_filename):
        modified = datetime.fromtimestamp(os.path.getmtime(vms_cache_filename))

    if modified < datetime.now() - timedelta(hours=int(config['sync_interval'])) or force:
        ps_script = "Get-VM * | Select Name,Id,State,Uptime | sort Name | ConvertTo-Json"
        rs = run_ps(ps_script)

        if rs.status_code != 0:
            print(rs.std_err)
            return False

        vms_json = json.loads(rs.std_out.decode('latin-1'))

        # If there is only one vm, make it a list
        if isinstance(vms_json, dict):
            vms_json = [vms_json]

        with open(vms_cache_filename, 'w') as vms_cache_file:
            json.dump(vms_json, vms_cache_file, indent=4)

    return True


def load_vms():
    """
    Loads current cache file into memory

    Returns:
        bool: True for success
    """
    global vms

    try:
        with open(vms_cache_filename, 'r') as vms_cache_file:
            vms = json.load(vms_cache_file)
    except IOError:
        print("Cannot access file {0}".format(vms_cache_filename))
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
    print("{0} {1} {2} {3}".format("Index".rjust(5),
                                   "State".ljust(7),
                                   "Name".ljust(30),
                                   "Uptime"))

    # Listing
    for vm in vms:
        index = str(vms.index(vm)).rjust(3)
        state = states.get(vm['State'], "unknown").ljust(7)
        name = str(vm['Name']).ljust(30)
        uptime = str(timedelta(hours=vm['Uptime']['TotalHours']))
        print("[{0}] {1} {2} {3}".format(index, state, name, uptime))


def list_vm_snaps(vm_index):
    """
    List vm snapshots by vm index

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = "Get-VMSnapshot -VMName {0} | Select Name,ParentSnapshotName,\
 CreationTime,ParentSnapshotId,Id | ConvertTo-Json".format(vm_name)

    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    try:
        snaps_json = json.loads(rs.std_out.decode('latin-1'))
    except Exception as e:
        print("Virtual Machine {} has no snapshots: {}".format(vm_name, e))
        return

    # If there is only one snap, make it a list
    if isinstance(snaps_json, dict):
        snaps_json = [snaps_json]

    t_snaps = create_tree(snaps_json, vm_name, f_pid="ParentSnapshotId",
                          f_id="Id",
                          f_label="Name",
                          f_ctime="CreationTime",
                          v_none=None)
    print("-- Virtual Machine Snapshots --")
    print(t_snaps)


def restore_vm_snap(vm_index, snap_name):
    """
    Restore virtual machine snapshot

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be restored

    Returns:
        bool: True if success
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = 'Restore-VMSnapshot -Name "{0}" -VMName {1} -Confirm:$false'.format(snap_name, vm_name)

    print('Restoring snapshot "{0}" in {1}'.format(snap_name, vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def remove_vm_snapshot(vm_index, snap_name, recursive=False):
    """
    Deletes a virtual machine checkpoint

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be deleted
        recursive (bool, optional): Specifies that the checkpoint’s children
            are to be deleted along with the checkpoint

    Returns:
        bool: True if success
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = 'Remove-VMSnapshot -VMName "{0}" -Name "{1}"'.format(vm_name,
                                                                     snap_name)
    if recursive:
        ps_script += " -IncludeAllChildSnapshots"
    ps_script += " -Confirm:$false"

    print('Removing snapshot "{0}" in "{1}"'.format(snap_name, vm_name))
    if recursive:
        print("and it's children")
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def create_vm_snapshot(vm_index, snap_name):
    """
    Create a new snapshot with vm's current state

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be created

    Returns:
        bool: True if success
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = 'Checkpoint-VM -Name "{0}" -SnapshotName "{1}" -Confirm:$false'.format(vm_name, snap_name)

    print('Creating snapshot "{0}" in "{1}"'.format(snap_name, vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def get_vm(vm_index):
    """
    Gets vm info by index

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    load_vms()

    vm_name = vms[vm_index]['Name']

    ps_script = "Get-VM -Name {0} | Select Name,Id,State | ConvertTo-Json".format(vm_name)
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return

    vm_json = json.loads(rs.std_out.decode('latin-1'))
    return vm_json


def stop_vm(vm_index, force=False):
    """
    Stop virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
        force (bool): Whether should force shutdown or not
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = "Stop-VM -Name {}".format(vm_name)
    if force:
        ps_script += " -Force"

    print('Stopping VM "{}", force: {}'.format(vm_name, force))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 3)
    print("Success")
    return True


def resume_vm(vm_index):
    """
    Resume (paused) virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = "Resume-VM -Name {0}".format(vm_name)

    print('Resuming VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 2)
    print("Success")
    return True


def pause_vm(vm_index):
    """
    Pause virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = "Suspend-VM -Name {0}".format(vm_name)

    print('Pausing VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 9)
    print("Success")
    return True


def start_vm(vm_index):
    """
    Start virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = "Start-VM -Name {0}".format(vm_name)

    print('Starting VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    update_cache(vm_index, 2)
    print("Success")
    return True


def setup(configp):
    """
    Setup hvclient globals and create protocol with server host and credentials

    Args:
        configp (dict): Configuration from config file
    """
    global config
    global vms_cache_filename

    config = configp
    vms_cache_filename = config['cache_file']


def run_ps(ps):
    """
    Run powershell script on target machine

    Args:
        ps (str): Powershell script to run
        proto (Protocol): Protocol containing target machine

    Returns:
        Response: Object containing stderr, stdout and exit_status
    """
    func_d = {'ssh': run_cmd_ssh,
              'winrm': run_cmd_winrm}
    proto = config['protocol']
    encoded_ps = b64encode(ps.encode('utf_16_le')).decode('ascii')
    rs = func_d[proto]('powershell -encodedcommand {0}'.format(encoded_ps))
    return rs


def run_cmd_ssh(cmd):
    """
    """
    ssh_client = SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.connect(username=config['user'],
                       password=config['pass'],
                       hostname=config['host'],
                       port=int(config['ssh_port']))

    rs = namedtuple('Response', ['std_out', 'std_err', 'status_code'])
    (sin, sout, serr) = ssh_client.exec_command(cmd)
    rs.std_out = sout.read()
    rs.std_err = serr.read()
    ssh_client.close()

    rs.status_code = 0
    if rs.std_err is not None:
        rs.status_code = 1

    return rs


def run_cmd_winrm(cmd):
    """
    Run batch script on target machine

    Args:
        cmd (str): batch script to run
        proto (Protocol): Protocol containing target machine

    Returns:
        Response: Object containing stderr, stdout and exit_status
    """
    client = Protocol(endpoint='http://{0}:5985/wsman'.format(config['host']),
                      transport='ntlm',
                      username='{0}\{1}'.format(config['domain'],
                                                config['user']),
                      password=config['pass'],
                      server_cert_validation='ignore')

    shell_id = client.open_shell()
    command_id = client.run_command(shell_id, cmd)
    rs = Response(client.get_command_output(shell_id, command_id))
    client.cleanup_command(shell_id, command_id)
    client.close_shell(shell_id)

    return rs
