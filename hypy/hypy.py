#!/usr/bin/env python3
# coding: utf-8

import configparser
import hvclient
import click


@click.group()
def main():
    """
    Multiplataform Hyper-V Manager using Python and FreeRDP
    """
    pass


@main.command("list", help='List virtual machines and its indexes')
@click.option('--sync', '-s', is_flag=True, help='Syncronize with server\
 updating local cache')
def list(sync):
    hvclient.update_all_cache(sync)
    hvclient.list_vms()


@main.command("ls", help='List updated virtual machines and its indexes')
@click.pass_context
def ls(ctx):
    ctx.invoke(list, sync=True)


@main.command(help='List virtual machine snapshots')
@click.argument('index')
def snaps(index):
    hvclient.list_vm_snaps(int(index))


@main.command(help='Restore virtual machine snapshot')
@click.argument('index')
@click.argument('snap_name')
def restore(index, snap_name):
    hvclient.restore_vm_snap(int(index), snap_name)


@main.command(help="Delete a machine's snapshot by name")
@click.argument('index')
@click.argument('snap_name')
@click.option('-r', is_flag=True, help="Remove snapshot's children as well")
def delete(index, snap_name, r):
    hvclient.remove_vm_snapshot(int(index), snap_name, r)


@main.command(help="Create a new snapshot with vm's current state")
@click.argument('index')
@click.argument('snap_name')
def create(index, snap_name):
    hvclient.create_vm_snapshot(int(index), snap_name)


@main.command(help="Connect to virtual machine identified by index")
@click.argument('index')
def connect(index):
    hvclient.connect(int(index))


@main.command(help='Start virtual machine identified by index')
@click.argument('index')
def start(index):
    hvclient.start_vm(int(index))


@main.command(help='Pause virtual machine identified by index')
@click.argument('index')
def pause(index):
    hvclient.pause_vm(int(index))


@main.command(help='Resume (paused) virtual machine identified by index')
@click.argument('index')
def resume(index):
    hvclient.resume_vm(int(index))


@main.command(help='Stop virtual machine identified by index')
@click.argument('index')
@click.option('--force', '-f', is_flag=True, help='Hyper-V gives the guest\
 five minutes to save data, then forces a shutdown')
def stop(index, force):
    hvclient.stop_vm(int(index), force)


def load_config():
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

        options = config['options']

        configuration['cache_file'] = options['cache_file']
        configuration['sync_interval'] = options['sync_interval']

        hvclient.setup(configuration)

    except KeyError:
        print("\n Please, configure your credentials file - hypy.conf")
        exit(1)


if __name__ == "__main__":
    load_config()
    main()
