import click
from hypy.modules import cache, hvclient, printer


@click.group('snap')
def snap():
    """Manage virtual machine snapshots"""
    pass


@snap.command('ls', help='List virtual machine snapshots')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
def snap_ls(by_name, ident):
    name = cache.get_name(by_name, ident)
    rs = hvclient.get_vm(name)
    vms = hvclient.parse_result(rs)
    cache.update_cache(vms)
    cache_vms = cache.list_vms()
    printer.print_list_vms(cache_vms, name)
    rs_snaps = hvclient.list_vm_snaps(name)
    snaps = hvclient.parse_result(rs_snaps)
    printer.print_vm_snaps(snaps, name, vms['ParentSnapshotName'])


@snap.command('create', help="Create a new snapshot with vm's current state")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.option('--snap_type',
              '-s',
              help='Snapshot type to be created',
              type=click.Choice(['standard', 'production']),
              default='standard')
@click.argument('snap_name')
def snap_create(by_name, ident, snap_name, snap_type):
    name = cache.get_name(by_name, ident)

    rs = hvclient.get_snapsshot_type(name)
    current_snap_type = hvclient.parse_result(rs)["CheckpointType"]

    if current_snap_type != hvclient.SNAP_TYPES[snap_type]:
        rs = hvclient.set_snapshot_type(name, snap_type)
        hvclient.parse_result(rs)

    rs = hvclient.create_vm_snapshot(name, snap_name)
    hvclient.parse_result(rs)


@snap.command('restore', help='Restore virtual machine snapshot')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.argument('snap_name')
def snap_restore(by_name, ident, snap_name):
    name = cache.get_name(by_name, ident)
    rs = hvclient.restore_vm_snap(name, snap_name)
    hvclient.parse_result(rs)


@snap.command('rm', help="Delete a machine's snapshot by name")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.option('-r', is_flag=True, help="Remove snapshot's children as well")
@click.argument('snap_name')
def snap_delete(by_name, r, ident, snap_name):
    name = cache.get_name(by_name, ident)
    rs = hvclient.remove_vm_snapshot(name, snap_name, r)
    hvclient.parse_result(rs)


#
# Aliases
#
@click.command('snaps', help='List virtual machine snapshots')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.pass_context
def snaps(ctx, by_name, ident):
    ctx.forward(snap_ls)


@click.command('create', help="Create a new snapshot with vm's current state")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.option('--snap_type',
              '-s',
              help='Snapshot type to be created',
              type=click.Choice(['standard', 'production']),
              default='standard')
@click.argument('snap_name')
@click.pass_context
def create(ctx, by_name, ident, snap_name, snap_type):
    ctx.forward(snap_create)


@click.command('restore', help='Restore virtual machine snapshot')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.argument('snap_name')
@click.pass_context
def restore(ctx, by_name, ident, snap_name):
    ctx.forward(snap_restore)


@click.command('delete', help="Delete a machine's snapshot by name")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
@click.option('-r', is_flag=True, help="Remove snapshot's children as well")
@click.argument('snap_name')
@click.pass_context
def delete(ctx, by_name, r, ident, snap_name):
    ctx.forward(snap_delete)
