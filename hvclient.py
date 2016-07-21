#!/usr/bin/env python
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

vms = None
server = None
config = None
vms_cache_filename = None
states = { 3 : 'off    ', 
           2 : 'running',
           9 : 'paused ',
           6 : 'saved  ' }

def connect(index):
    """
    Connect to virtual machine by index using freerdp
    """
    load_vms()

    vm_id = vms[index]['Id']

    user = config['user']
    passw = config['pass']
    host = config['host']

    cmd = ['xfreerdp', '/v:{0}'.format(host), '/vmconnect:{0}'.format(vm_id), '/u:{0}'.format(user), '/p:{0}'.format(passw)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    retval = p.wait()

    if retval != 0:
        print("Starting machine {0}".format(index))
        start_vm(index)
        time.sleep(2)
        connect(index)

def update_cache(force=False):
    """
    Checks cache file modification time and update vm list
    Creates cache file if nonexistent
    """
    modified = datetime.min
    if os.path.isfile(vms_cache_filename):
        modified = datetime.fromtimestamp(os.path.getmtime(vms_cache_filename))

    if modified < datetime.now() - timedelta(hours = int(config['sync_interval'])) or force:
        ps_script = "Get-VM * | Select Name,Id,State | ConvertTo-Json"
        rs = run_ps(ps_script, server)

        if rs.status_code != 0:
            print(rs.std_err)
            return False

        vms_json = json.loads(rs.std_out.decode('utf-8'))
        with open(vms_cache_filename, 'w') as vms_cache_file:
            json.dump(vms_json, vms_cache_file, indent=4)

    return True

def load_vms():
    """
    Loads current cache file into memory
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
    for vm in vms:
        #print("[{0}] {1} {2} {3}".format(vms.index(vm), states[vm['State']], vm['Name'], vm['Id']))
        print("[{0}] {1} {2}".format(str(vms.index(vm)).rjust(3), states[vm['State']], vm['Name']))

def list_vm_snapshots(p, vm_index):
    """
    List vm snapshots by vm index
    """
    load_vms()

    vm_name = vms[vm_index]['Name']
    ps_script = "Get-VM {0} | Get-VMSnapshot | Select Name,ParentSnapshotName | ConvertTo-Json".format(vm_name)

    rs = run_ps(ps_script, p)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    snaps_json = json.loads(rs.std_out)
    print(snaps_json)
    #for snap in snaps_json:
        #print snap


def stop_vm(vm_index):
    """
    Stop virtual machine
    """
    load_vms()

    vm_name = vms[vm_index]['Name']

    ps_script = "Stop-VM {0}".format(vm_name)
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print( rs.std_err)
        return False

    return True

def start_vm(vm_index):
    """
    Start virtual machine
    """
    load_vms()

    vm_name = vms[vm_index]['Name']

    ps_script = "Start-VM {0}".format(vm_name)
    rs = run_ps(ps_script, server)

    if rs.status_code != 0:
        print(rs.std_err)
        return False

    return True

def setup(configp):
    global config
    global server
    global vms_cache_filename

    config = configp

    domain = config['domain']
    user = config['user']
    passw = config['pass']
    host = config['host']
    vms_cache_filename = config['cache_file']

    #print('Setando server')
    server = Protocol(endpoint='http://{0}:5985/wsman'.format(host),
                 transport='ntlm',
                 username='{0}\{1}'.format(domain,user),
                 password=passw,
                 server_cert_validation='ignore')

def run_ps(ps, proto):
    encoded_ps = b64encode(ps.encode('utf_16_le')).decode('ascii')
    rs = run_cmd('powershell -encodedcommand {0}'.format(encoded_ps), proto)
    return rs

def run_cmd(cmd, proto):
    shell_id = proto.open_shell()
    command_id = proto.run_command(shell_id, cmd)
    rs = Response(proto.get_command_output(shell_id, command_id))
    proto.cleanup_command(shell_id, command_id)
    proto.close_shell(shell_id)
    return rs

