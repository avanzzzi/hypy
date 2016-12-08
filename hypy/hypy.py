#!/usr/bin/env python3
# coding: utf-8

import configparser
import hvclient
import click
import base64
import time

@click.group()
def main():
    """
    Multiplataform Hyper-V Manager using Python and FreeRDP
    """
    pass


@main.command(help='List virtual machines and its indexes')
@click.option('--sync', '-s', is_flag=True, help='Syncronize with server updating local cache')
def list(sync):
    hvclient.update_all_cache(sync)
    hvclient.list_vms()


@main.command(help='List virtual machine snapshots')
@click.option('--name', '-n', help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def snaps(name, index):
    hvclient.list_vm_snaps(int(index), name)


@main.command(help='List and set network adpater configuration from vm')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
@click.option('--setswitch', '-s', default="", help='Vm´s name')
@click.option('--tbefore', '-n', default=3, help='Time to wait in seconds before start')
@click.option('--tafter', '-n', default=3, help='Time to wait in seconds after completed')
def network(name, index, setswitch, tbefore, tafter):
    time.sleep(tbefore)
    if setswitch != "":
        hvclient.set_vm_switch(int(index), setswitch, name)
        time.sleep(tafter)

    hvclient.get_vm_network(int(index), name)


@main.command(help='List hyper-v switches available')
def switches():
    hvclient.load_switches()


@main.command(help='Restore virtual machine snapshot by name or index')
@click.argument('snap_name')
@click.option('--name', '-n', default="", help='Vm´s name to be restored')
@click.option('--force', '-f', is_flag=True, help='Forces a restore and start if necessary')
@click.option('--cache', '-c', is_flag=True, help='For not use cache file based')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def restore(snap_name, name, force, cache, index):
    hvclient.restore_vm_snap(index, snap_name, vm_name=name, force=force, no_cache=cache)


@main.command(help="Delete a machine's snapshot by name using vm´s name")
@click.option('--snap', '-s', help='snap name ')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('-r', is_flag=True, help="Remove snapshot's children as well")
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def delete(snap, name, r, index):
    hvclient.remove_vm_snapshot(index, snap, r, name)


@main.command(help="Create a new snapshot with vm's current state using vm´s name")
@click.option('--snap', '-s', help='snap name ')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def create(snap, name, index):
    hvclient.create_vm_snapshot(int(index), snap, name)


@main.command(help="Connect to virtual machine identified by index")
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def connect(index):
    hvclient.connect(int(index))


@main.command(help='Start virtual machine identified by it´s name')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def start(name, index):
    hvclient.start_vm(int(index), name)


@main.command(help='Pause virtual machine identified by it´s name')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def pause(name, index):
    hvclient.pause_vm(index, name)


@main.command(help='Resume (paused) virtual machine identified by it´s name')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def resume(name, index):
    hvclient.resume_vm(int(index), name)


@main.command(help='Stop virtual machine identified by its name')
@click.option('--name', '-n', default="", help='Vm´s name')
@click.option('--force', '-f', is_flag=True, help='Hyper-V gives the guest five minutes to save data, then forces a shutdown')
@click.option('--index', '-i', default=-1, help='Index optional for vm')
def stop(name, force, index):
    hvclient.stop_vm(index, force, name)


def load_config():
    """
    Read config file and sends the resultant dict to setup hvclient
    TODO: Validate options
    """
    try:
        config = configparser.ConfigParser()
        config.read('hypy.conf')

        credentials = config['credentials']

        configuration = {'user': bytes.decode(base64.b64decode(credentials['user'].encode())) , 'pass': bytes.decode(base64.b64decode(credentials['pass'].encode())), 'domain': credentials['domain'],
                         'host': credentials['host']}

        options = config['options']

        configuration['cache_file'] = options['cache_file']
        configuration['sync_interval'] = options['sync_interval']

        hvclient.setup(configuration)

    except KeyError:
        print ("\n Please, configure your credentials file - hypy.conf")
        exit()


if __name__ == "__main__":
    load_config()
    main()
    exit(0)
