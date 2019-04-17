from time import sleep

import click
from hypy.modules import cache, config, hvclient, printer


@click.group('cli')
@click.option('--user', '-u', help='Username in hyper-v server')
@click.option('passw', '--pass', '-p', help='Password in hyper-v server')
@click.option('--domain', '-d', help='Domain name')
@click.option('--host', '-m', help='Hyper-V server hostname/ip address')
@click.option('--proto', '-t', help='Protocol to be used',
              type=click.Choice(['ssh', 'winrm']))
def cli(user, passw, domain, host, proto):
    """
    Multiplataform Hyper-V Manager using Python and FreeRDP
    """
    config.load(user, passw, domain, host, proto)
    hvclient.config = config.configuration
    cache.current_host = config.configuration['host']
    cache.sync_interval = config.configuration['sync_interval']


@cli.command("status", help='Show virtual machine current status')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def show_status(ctx, by_name, ident):
    name = cache.get_name(by_name, ident)
    rs = hvclient.get_vm(name)
    vms = hvclient.parse_result(rs)
    cache.update_cache(vms)
    cache_vms = cache.list_vms()
    printer.print_list_vms(cache_vms, name)
    rs_snaps = hvclient.list_vm_snaps(name)
    snaps = hvclient.parse_result(rs_snaps)
    printer.print_vm_snaps(snaps, name, vms['ParentSnapshotName'])


@cli.command("list", help='List virtual machines and its indexes')
@click.option('--sync', '-s', is_flag=True, default=False,
              help='Syncronize with server updating local cache')
@click.option('--name', '-n', help='Filter virtual machines by name')
@click.option('--rem', '-r', is_flag=True, default=False, help='Remove old cache before sync')
def list_vms(sync, name, rem):
    remove_old_cache = rem or cache.need_update()
    if sync or remove_old_cache:
        rs = hvclient.get_vm(name)
        vms = hvclient.parse_result(rs)
        if remove_old_cache:
            cache.remove_cache()
        cache.update_cache(vms)
    cache_vms = cache.list_vms()
    printer.print_list_vms(cache_vms, name)


@cli.command("ls", help='List updated virtual machines and its indexes')
@click.option('--name', '-n', help='Filter virtual machines by name')
@click.option('--rem', '-r', is_flag=True, default=False, help='Remove old cache before sync')
@click.pass_context
def ls(ctx, name, rem):
    ctx.invoke(list_vms, sync=True, name=name, rem=rem)


@cli.command(help="Connect to virtual machine identified by index")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
def connect(by_name, ident):
    name = cache.get_name(by_name, ident)
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


@cli.command(help='Start virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def start(ctx, by_name, ident):
    name = cache.get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.start_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@cli.command(help='Pause virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def pause(ctx, by_name, ident):
    name = cache.get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.pause_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@cli.command(help='Resume (paused) virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def resume(ctx, by_name, ident):
    name = cache.get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.resume_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@cli.command(help='Stop virtual machine identified by index')
@click.option('--force', '-f', is_flag=True, help='Hyper-V gives the guest\
 five minutes to save data, then forces a shutdown')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def stop(ctx, by_name, ident, force):
    name = cache.get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.stop_vm(name, force)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)


@cli.command(help='Save virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def save(ctx, by_name, ident):
    name = cache.get_name(by_name, ident)
    ctx.invoke(list_vms, sync=False, name=name)
    rs = hvclient.save_vm(name)
    hvclient.parse_result(rs)
    ctx.invoke(list_vms, sync=True, name=name)
