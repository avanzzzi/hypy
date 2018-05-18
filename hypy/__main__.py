#!/usr/bin/env python3
# coding: utf-8
from time import sleep

import click

from hypy.modules import cache, config, hvclient, printer


@click.group()
@click.option('--user', '-u', help='Username in hyper-v server')
@click.option('passw', '--pass', '-p', help='Password in hyper-v server')
@click.option('--domain', '-d', help='Domain name')
@click.option('--host', '-m', help='Hyper-V server hostname/ip address')
@click.option('--proto', '-t', help='Protocol to be used',
              type=click.Choice(['ssh', 'winrm']))
def main(user, passw, domain, host, proto):
    """
    Multiplataform Hyper-V Manager using Python and FreeRDP
    """
    config.load(user, passw, domain, host, proto)
    hvclient.config = config.configuration
    cache.current_host = config.configuration['host']
    cache.sync_interval = config.configuration['sync_interval']


@main.command("status", help='Show virtual machine current status')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def show_status(ctx, by_name, ident):
    ctx.invoke(snaps, by_name=by_name, ident=ident)


@main.command("list", help='List virtual machines and its indexes')
@click.option('--sync', '-s', is_flag=True, default=False,
              help='Syncronize with server updating local cache')
@click.option('--name', '-n', help='Filter virtual machines by name')
def list_vms(sync, name):
    if sync or cache.need_update():
        rs = hvclient.get_vm(name)
        vms = hvclient.parse_result(rs)
        cache.update_cache(vms)
    cache_vms = cache.list_vms()
    printer.print_list_vms(cache_vms, name)


@main.command("ls", help='List updated virtual machines and its indexes')
@click.option('--name', '-n', help='Filter virtual machines by name')
@click.pass_context
def ls(ctx, name):
    ctx.invoke(list_vms, sync=True, name=name)


@main.command(help='List virtual machine snapshots')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
def snaps(by_name, ident):
    name = get_name(by_name, ident)
    rs = hvclient.get_vm(name)
    vms = hvclient.parse_result(rs)
    cache.update_cache(vms)
    cache_vms = cache.list_vms()
    printer.print_list_vms(cache_vms, name)
    rs_snaps = hvclient.list_vm_snaps(name)
    snaps = hvclient.parse_result(rs_snaps)
    printer.print_vm_snaps(snaps, name, vms['ParentSnapshotName'])


@main.command(help='Restore virtual machine snapshot')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.argument('snap_name')
def restore(by_name, ident, snap_name):
    name = get_name(by_name, ident)
    rs = hvclient.restore_vm_snap(name, snap_name)
    hvclient.parse_result(rs)


@main.command(help="Delete a machine's snapshot by name")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.option('-r', is_flag=True, help="Remove snapshot's children as well")
@click.argument('snap_name')
def delete(by_name, r, ident, snap_name):
    name = get_name(by_name, ident)
    rs = hvclient.remove_vm_snapshot(name, snap_name, r)
    hvclient.parse_result(rs)


@main.command(help="Create a new snapshot with vm's current state")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.option('--snap_type',
              '-s',
              help='Snapshot type to be created',
              type=click.Choice(['standard', 'production']),
              default='standard')
@click.argument('snap_name')
def create(by_name, ident, snap_name, snap_type):
    name = get_name(by_name, ident)

    rs = hvclient.get_snapsshot_type(name)
    current_snap_type = hvclient.parse_result(rs)["CheckpointType"]

    if current_snap_type != hvclient.SNAP_TYPES[snap_type]:
        rs = hvclient.set_snapshot_type(name, snap_type)
        hvclient.parse_result(rs)

    rs = hvclient.create_vm_snapshot(name, snap_name)
    hvclient.parse_result(rs)


@main.command(help="Connect to virtual machine identified by index")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
def connect(by_name, ident):
    name = get_name(by_name, ident)
    vm_cache = cache.get_vm_by_name(name)

    vm_name = vm_cache['Name']
    vm_index = vm_cache['index']
    vm_id = vm_cache['Id']

    rs = hvclient.get_vm(vm_name)
    vm = hvclient.parse_result(rs)
    cache.update_cache(vm)

    if vm['State'] not in [2, 9]:
        rs = hvclient.start_vm(vm_name)
        hvclient.parse_result(rs)
        sleep(5)

    hvclient.connect(vm_id, vm_name, vm_index)


@main.command(help='Start virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def start(ctx, by_name, ident):
    name = get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.start_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@main.command(help='Pause virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def pause(ctx, by_name, ident):
    name = get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.pause_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@main.command(help='Resume (paused) virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def resume(ctx, by_name, ident):
    name = get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.resume_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@main.command(help='Stop virtual machine identified by index')
@click.option('--force', '-f', is_flag=True, help='Hyper-V gives the guest\
 five minutes to save data, then forces a shutdown')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def stop(ctx, by_name, ident, force):
    name = get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.stop_vm(name, force)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@main.command(help='Save virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def save(ctx, by_name, ident):
    name = get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.save_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@main.group('switch')
def switch():
    """Manage virtual network switches in the Hyper-V server."""
    pass


@main.command('switches', help='List avaiable virtual network switches in the Hyper-V server')
@click.pass_context
def switches(ctx):
    ctx.invoke(list_switches)


@switch.command('ls', help='List avaiable virtual network switches in the Hyper-V server')
def list_switches():
    rs = hvclient.list_switches()
    switches = hvclient.parse_result(rs)
    printer.print_switches(switches)


@switch.command('set', help='Change current vm network switch')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.argument('switch_name')
def set_switch(by_name, ident, switch_name):
    pass


@switch.command('get', help='Get current vm network switch')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
def get_switch(by_name, ident):
    pass


def get_name(by_name, ident):
    """Retrieve name or name by index based on user input."""
    if by_name:
        name = ident
    else:
        index = ident
        name = cache.get_vm_by_index(index)['Name']

    return name


if __name__ == '__main__':
    main()
