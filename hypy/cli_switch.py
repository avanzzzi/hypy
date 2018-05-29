import click
from hypy.modules import cache, hvclient, printer


@click.group('switch')
def switch():
    """Manage virtual network switches in the Hyper-V server."""
    pass


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
    name = cache.get_name(by_name, ident)
    rs = hvclient.set_switch(name, switch_name)
    hvclient.parse_result(rs)


@switch.command('get', help='Get current vm network switch')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('ident')
def get_switch(by_name, ident):
    name = cache.get_name(by_name, ident)
    rs = hvclient.get_switch(name)
    switch = hvclient.parse_result(rs)
    printer.print_vm_switch(switch)


#
# Aliases
#
@click.command('switches', help='List avaiable virtual network switches in the Hyper-V server')
@click.pass_context
def switches(ctx):
    ctx.forward(list_switches)
