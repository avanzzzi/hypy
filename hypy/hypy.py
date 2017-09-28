#!/usr/bin/env python3
# coding: utf-8

import configparser
import click
from modules import hvclient
from modules import printer
from modules import cache


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
    load_config(user, passw, domain, host, proto)


@main.command("list", help='List virtual machines and its indexes')
@click.option('--sync', '-s', is_flag=True, default=False,
              help='Syncronize with server updating local cache')
@click.option('--name', '-n', help='Use vm name instead of index')
def list_vms(sync, name):
    rs = hvclient.get_vms(name)
    vms = hvclient.parse_result(rs)
    cache.update_cache(vms)
    cache_vms = cache.cache_list_vms()
    printer.print_list_vms(cache_vms)


@main.command("ls", help='List updated virtual machines and its indexes')
@click.pass_context
def ls(ctx):
    ctx.invoke(list_vms, sync=True)


@main.command(help='List virtual machine snapshots')
@click.option('--name', '-n', help='Use vm name instead of index')
@click.argument('index', required=False)
@click.pass_context
def snaps(ctx, name, index):
    if not (name or index) or (name and index):
        click.echo(ctx.get_help())
        return

    vm_name, rs = hvclient.list_vm_snaps(name, index)
    printer.print_vm_snaps(vm_name, rs)


@main.command(help='Restore virtual machine snapshot')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('index')
@click.argument('snap_name')
def restore(by_name, index, snap_name):
    hvclient.restore_vm_snap(by_name, index, snap_name)


@main.command(help="Delete a machine's snapshot by name")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.option('-r', is_flag=True, help="Remove snapshot's children as well")
@click.argument('index')
@click.argument('snap_name')
def delete(by_name, index, snap_name, r):
    hvclient.remove_vm_snapshot(by_name, index, snap_name, r)


@main.command(help="Create a new snapshot with vm's current state")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('index')
@click.argument('snap_name')
def create(by_name, index, snap_name):
    hvclient.create_vm_snapshot(by_name, index, snap_name)


@main.command(help="Connect to virtual machine identified by index")
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('index')
def connect(by_name, index):
    hvclient.connect(by_name, index)


@main.command(help='Start virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('index')
def start(by_name, index):
    hvclient.start_vm(by_name, index)


@main.command(help='Pause virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('index')
def pause(by_name, index):
    hvclient.pause_vm(by_name, index)


@main.command(help='Resume (paused) virtual machine identified by index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.argument('index')
def resume(by_name, index):
    hvclient.resume_vm(by_name, index)


@main.command(help='Stop virtual machine identified by index')
@click.argument('index')
@click.option('--name', '-n', 'by_name', is_flag=True, default=False,
              help='Use vm name instead of index')
@click.option('--force', '-f', is_flag=True, help='Hyper-V gives the guest\
 five minutes to save data, then forces a shutdown')
def stop(by_name, index, force):
    hvclient.stop_vm(by_name, index, force)


def load_config(user, passw, domain, host, proto):
    """
    Read config file and sends the resultant dict to setup hvclient
    TODO: Validate options
    """
    try:
        config = configparser.ConfigParser()
        config.read('hypy.conf')

        credentials = config['credentials']

        configuration = {'user': credentials['user'],
                         'pass': credentials['pass'],
                         'domain': credentials['domain'],
                         'host': credentials['host']}

        if user is not None:
            configuration['user'] = user
        if passw is not None:
            configuration['pass'] = passw
        if domain is not None:
            configuration['domain'] = domain
        if host is not None:
            configuration['host'] = host

        options = config['options']

        configuration['cache_file'] = options['cache_file']
        configuration['sync_interval'] = options['sync_interval']
        configuration['protocol'] = options['protocol']
        configuration['ssh_port'] = options['ssh_port']

        if proto is not None:
            configuration['protocol'] = proto

        hvclient.setup(configuration)

    except KeyError:
        print("Please, configure your credentials file - hypy.conf")
        exit(1)


if __name__ == "__main__":
    main()
