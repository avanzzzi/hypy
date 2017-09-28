#!/usr/bin/env python3
# coding: utf-8

import json
import time
import platform
from collections import namedtuple
from paramiko import SSHClient, AutoAddPolicy
from subprocess import Popen, DEVNULL
from winrm import Protocol
from winrm import Response
from base64 import b64encode

config = None


def connect(by_name, index):
    """
    Connect to virtual machine by index using freerdp

    Args:
        index (int): The machine's index generated in the current cache
    """
    vms = load_vms_from_cache()
    if by_name:
        vm_id = [vm['Id'] for vm in vms if vm['Name'] == index][0]
    else:
        vm_id = vms[int(index)]['Id']

    user = config['user']
    passw = config['pass']
    host = config['host']

    vm_info = get_vm(by_name, index)
    if vm_info != '' and vm_info['State'] != 2 and vm_info['State'] != 9:
        start_vm(by_name, index)
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


def get_vms(vm_name):
    """
    """
    ps_script = "Get-VM -Name {} | Select Name,Id,State,Uptime | sort Name | ConvertTo-Json".format(vm_name)
    rs = run_ps(ps_script)

    return rs


def list_vms(sync):
    """
    List virtual machines
    """
    vms = load_vms_from_cache()

    return vms


def list_vm_snaps(vm_name, vm_index):
    """
    List vm snapshots.

    Args:
        vm_name (str): The virtual machine name
        vm_index (int): The machine's index generated in the current cache
    """
    if vm_index:
        vms = load_vms_from_cache()
        vm_name = vms[int(vm_index)]['Name']

    ps_script = "Get-VMSnapshot -VMName {0} | Select Name,ParentSnapshotName,CreationTime,ParentSnapshotId,Id | ConvertTo-Json".format(vm_name)

    rs = run_ps(ps_script)
    return vm_name, rs


def restore_vm_snap(by_name, index, snap_name):
    """
    Restore virtual machine snapshot

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be restored

    Returns:
        bool: True if success
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = 'Restore-VMSnapshot -Name "{0}" -VMName {1} -Confirm:$false'.format(snap_name, vm_name)

    print('Restoring snapshot "{0}" in {1}'.format(snap_name, vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def remove_vm_snapshot(by_name, index, snap_name, recursive=False):
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
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

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


def create_vm_snapshot(by_name, index, snap_name):
    """
    Create a new snapshot with vm's current state

    Args:
        vm_index (int): The machine's index generated in the current cache
        snap_name (str): The name of the checkpoint to be created

    Returns:
        bool: True if success
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = 'Checkpoint-VM -Name "{0}" -SnapshotName "{1}" -Confirm:$false'.format(vm_name, snap_name)

    print('Creating snapshot "{0}" in "{1}"'.format(snap_name, vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def parse_result(rs):
    if rs.status_code != 0:
        print(rs.std_err)
        return False

    try:
        rs_json = json.loads(rs.std_out.decode('latin-1'))
    except Exception as e:
        print("Error parsing remote response: {}".format(e))
        return False

    # If there is only one snap, make it a list
    if isinstance(rs_json, dict):
        rs_json = [rs_json]

    return rs_json


def get_vm(by_name, index):
    """
    Gets vm info by index

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = "Get-VM -Name {0} | Select Name,Id,State | ConvertTo-Json".format(vm_name)
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return

    vm_json = json.loads(rs.std_out.decode('latin-1'))
    return vm_json


def stop_vm(by_name, index, force=False):
    """
    Stop virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
        force (bool): Whether should force shutdown or not
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = "Stop-VM -Name {}".format(vm_name)
    if force:
        ps_script += " -Force"

    print('Stopping VM "{}", force: {}'.format(vm_name, force))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def resume_vm(by_name, index):
    """
    Resume (paused) virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = "Resume-VM -Name {0}".format(vm_name)

    print('Resuming VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def pause_vm(by_name, index):
    """
    Pause virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = "Suspend-VM -Name {0}".format(vm_name)

    print('Pausing VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    print("Success")
    return True


def start_vm(by_name, index):
    """
    Start virtual machine

    Args:
        vm_index (int): The machine's index generated in the current cache
    """
    if by_name:
        vm_name = index
    else:
        vms = load_vms_from_cache()
        vm_name = vms[int(index)]['Name']

    ps_script = "Start-VM -Name {0}".format(vm_name)

    print('Starting VM "{0}"'.format(vm_name))
    rs = run_ps(ps_script)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

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
    Run batch script using ssh client.

    Args:
        cmd (str): batch script to run

    Returns:
        Response: Object containing stderr, stdout and exit_status
    """
    ssh_client = SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(username=config['user'],
                       password=config['pass'],
                       hostname=config['host'],
                       port=int(config['ssh_port']))

    (sin, sout, serr) = ssh_client.exec_command(cmd)

    rs = namedtuple('Response', ['std_out', 'std_err', 'status_code'])
    rs.std_out = sout.read()
    rs.std_err = serr.read()
    rs.status_code = sout.channel.recv_exit_status()
    ssh_client.close()

    return rs


def run_cmd_winrm(cmd):
    """
    Run batch script using winrm client.

    Args:
        cmd (str): batch script to run

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
