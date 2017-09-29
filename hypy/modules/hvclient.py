import json
import platform
from collections import namedtuple
from paramiko import SSHClient, AutoAddPolicy
from subprocess import Popen, DEVNULL
from winrm import Protocol
from winrm import Response
from base64 import b64encode

config = None


def connect(vm_name: str, vm_id: str, vm_index: str):
    """
    Connect to the virtual machine.

    Args:
        vm_name: Name of the vm to connect.
        vm_id: Hyper-v unique identificator of the vm.
        vm_index: Index of the vm in the cache file.
    """
    user = config['user']
    passw = config['pass']
    host = config['host']

    if platform.uname()[0] == "Windows":
        freerdp_bin = "wfreerdp.exe"
    else:
        freerdp_bin = "xfreerdp"

    cmd = [freerdp_bin, '/v:{0}'.format(host),
                        '/vmconnect:{0}'.format(vm_id),
                        '/u:{0}'.format(user),
                        '/p:{0}'.format(passw),
                        '/t:{} [{}] {}'.format(host, vm_index, vm_name),
                        '/cert-ignore']

    try:
        Popen(cmd, stdout=DEVNULL, stderr=DEVNULL)
    except FileNotFoundError as err:
        print("{} not found in PATH\n{}".format(freerdp_bin, err))


def get_vm(vm_name: str) -> Response:
    """
    Retrieve vm information from hyper-v.

    Args:
        vm_name: Name of the vm. Using * in the vm's name can retrieve info
            of one or more machines. If the vm_name is None, * will be used
            instead, gathering information about all vms in the host which can
            be slow depending on the number of vms.
    Returns:
        Info obtained from remove hyper-v host.
    """
    if not vm_name:
        vm_name = '*'
    ps_script = "Get-VM -Name {} | Select Name,Id,State,Uptime | sort Name | ConvertTo-Json".format(vm_name)
    rs = run_ps(ps_script)

    return rs


def list_vm_snaps(vm_name: str) -> Response:
    """
    List vm snapshots.

    Args:
        vm_name: The virtual machine name.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = "Get-VMSnapshot -VMName {0} | Select Name,ParentSnapshotName,CreationTime,ParentSnapshotId,Id | ConvertTo-Json".format(vm_name)

    rs = run_ps(ps_script)
    return rs


def restore_vm_snap(vm_name: str, snap_name: str) -> Response:
    """
    Restore virtual machine snapshot.

    Args:
        vm_name: The virtual machine name.
        snap_name: The name of the checkpoint to be restored.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = 'Restore-VMSnapshot -Name "{0}" -VMName {1} -Confirm:$false'.format(snap_name, vm_name)

    rs = run_ps(ps_script)
    return rs


def remove_vm_snapshot(vm_name: str, snap_name: str,
                       recursive: bool=False) -> Response:
    """
    Deletes a virtual machine checkpoint.

    Args:
        vm_name: The virtual machine name.
        snap_name: The name of the checkpoint to be deleted.
        recursive: Specifies that the checkpoint’s children
            are to be deleted along with the checkpoint.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = 'Remove-VMSnapshot -VMName "{0}" -Name "{1}"'.format(vm_name,
                                                                     snap_name)
    if recursive:
        ps_script += " -IncludeAllChildSnapshots"
    ps_script += " -Confirm:$false"

    rs = run_ps(ps_script)
    return rs


def create_vm_snapshot(vm_name: str, snap_name: str) -> Response:
    """
    Create a new snapshot with vm's current state.

    Args:
        vm_name: The virtual machine name.
        snap_name: The name of the checkpoint to be created.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = 'Checkpoint-VM -Name "{0}" -SnapshotName "{1}" -Confirm:$false'.format(vm_name, snap_name)

    rs = run_ps(ps_script)
    return rs


def parse_result(rs: Response) -> dict:
    """
    Parse Respnse object obtained from hyper-v.

    Args:
        rs: Response object with its properties (out, err and return_code).
    Returns:
        Normalized information about the vm(s).
    """
    if rs.status_code != 0:
        print(rs.std_err)
        return False

    try:
        rs_json = json.loads(rs.std_out.decode('latin-1'))
    except Exception as e:
        print("Error parsing remote response: {}".format(e))
        return False

    # If there is only one element, make it a list
    if isinstance(rs_json, dict):
        rs_json = [rs_json]

    return rs_json


def stop_vm(vm_name: str, force: bool=False) -> Response:
    """
    Stop virtual machine.

    Args:
        vm_name: The virtual machine name.
        force: Whether should force shutdown or not.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = "Stop-VM -Name {}".format(vm_name)
    if force:
        ps_script += " -Force"

    rs = run_ps(ps_script)
    return rs


def resume_vm(vm_name: str) -> Response:
    """
    Resume (paused) virtual machine.

    Args:
        vm_name: The virtual machine name.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = "Resume-VM -Name {0}".format(vm_name)

    rs = run_ps(ps_script)
    return rs


def pause_vm(vm_name: str) -> Response:
    """
    Pause virtual machine.

    Args:
        vm_name: The virtual machine name.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = "Suspend-VM -Name {0}".format(vm_name)

    rs = run_ps(ps_script)
    return rs


def start_vm(vm_name: str) -> Response:
    """
    Start virtual machine.

    Args:
        vm_name: The virtual machine name.
    Returns:
        Info obtained from remove hyper-v host.
    """
    ps_script = "Start-VM -Name {0}".format(vm_name)
    rs = run_ps(ps_script)

    return rs


def run_ps(ps: str) -> Response:
    """
    Run powershell script on target machine.

    Args:
        ps: Powershell script to run.
    Returns:
        Response object containing stderr, stdout and exit_status.
    """
    func_d = {'ssh': run_cmd_ssh,
              'winrm': run_cmd_winrm}
    proto = config['protocol']
    encoded_ps = b64encode(ps.encode('utf_16_le')).decode('ascii')
    rs = func_d[proto]('powershell -encodedcommand {0}'.format(encoded_ps))
    return rs


def run_cmd_ssh(cmd: str) -> Response:
    """
    Run batch script using ssh client.

    Args:
        cmd: batch script to run.
    Returns:
        Response object containing stderr, stdout and exit_status.
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


def run_cmd_winrm(cmd: str) -> Response:
    """
    Run batch script using winrm client.

    Args:
        cmd: batch script to run.
    Returns:
        Response object containing stderr, stdout and exit_status.
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
