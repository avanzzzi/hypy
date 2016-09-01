# HYPY - HYper-v in PYthon
Multiplataform Hyper-V Manager using Python and FreeRDP

## How HYPY works?
Hypy uses winrm to comunicate with hyper-v server shell and sends powershell commands to interact with the virtual machines. Using Powershell, HYPY can get Name, ID and state of virtual machines. Therefore, HYPY call freeRDP with vm-id and credentials, using settings in `.conf` file to connect the vm.

## Pre-requisites
### WinRM
Hypy uses winrm to communicate with the hyper-v host, so it must be enabled and accepting connections.
https://github.com/diyan/pywinrm has a session explaining how to Enable WinRM on the remote host.

### FreeRDP
FreeRDP binary must be in path (windows, linux and mac). Make sure FreeRDP is working before using hypy or it will not open the session to the virtual machine.
If you are using Linux, you package manager should have freerdp avaiable or look into https://github.com/FreeRDP/FreeRDP for install instructions.

## Configuration
To configure Hypy, change the file 'hypy.conf'
```ini
[credentials]
host = <server name in domain>
domain = <domain name>
user = <user name in server>
pass = <password>

[options]
cache_file = <name of cache file>
sync_interval = <interval in hours to make new cache file>
```
You must have write permissions to the path pointed by cache_file

## usage
If you don't know how to use hypy, you can use `hypy.py --help`
```
hypy.py --help
  Usage: hypy.py [OPTIONS] COMMAND [ARGS]...

  Multiplataform Hyper-V Manager using Python and FreeRDP

Options:
  --help  Show this message and exit.

Commands:
  connect  Connect to virtual machine identified by...
  create   Create a new snapshot with vm's current state
  delete   Delete a machine's snapshot by name
  list     List virtual machines and its indexes
  pause    Pause virtual machine identified by index
  restore  Restore virtual machine snapshot
  resume   Resume (paused) virtual machine identified by...
  snaps    List virtual machine snapshots
  start    Start virtual machine identified by index
  stop     Stop virtual machine identified by index
```
If you need help on any subcommand, run `hypy.py COMMAND --help`

### list
```
hypy.py list --help
Usage: hypy.py list [OPTIONS]

  List virtual machines and its indexes

Options:
  -s, --sync  Syncronize with server updating local cache
  --help      Show this message and exit.
```
Hypy will create a cache with indexes for each machine. These indexes are used by other hypy commands to interact with the virtual machines.
If your cache is older than the duration specified in sync_interval, a new cache will be created, so the machine's states will be updated.
To force an cache update use the sync parameter.

A machine listing would look like this:
```
[01]    Machine 01
[02]    Machine 02
[03]    Machine 03
[04]    Machine 04
[05]    Machine 05
[06]    Machine 06
[07]    Machine 07
[08]    Machine 08
[09]    Machine 09
[10]    Machine 10
```
### connect
```
hypy connect --help
Usage: hypy.py connect [OPTIONS] INDEX

  Connect to virtual machine identified by index

Options:
  --help  Show this message and exit.
```
### create
```
hypy create --help
Usage: hypy.py create [OPTIONS] INDEX SNAP_NAME

  Create a new snapshot with vm's current state

Options:
  --help  Show this message and exit.
```
### delete
```
hypy delete --help
Usage: hypy.py delete [OPTIONS] INDEX SNAP_NAME

  Delete a machine's snapshot by name

Options:
  -r      Remove snapshot's children as well
  --help  Show this message and exit.
```
### restore
```
hypy restore --help
Usage: hypy.py restore [OPTIONS] INDEX SNAP_NAME

  Restore virtual machine snapshot

Options:
  --help  Show this message and exit.
```
### snaps
```
hypy snaps --help
Usage: hypy.py snaps [OPTIONS] INDEX

  List virtual machine snapshots

Options:
  --help  Show this message and exit
```
### start
```
hypy start --help
Usage: hypy.py start [OPTIONS] INDEX

  Start virtual machine identified by index

Options:
  --help  Show this message and exit.
```
### stop
```
hypy stop --help
Usage: hypy.py stop [OPTIONS] INDEX

  Stop virtual machine identified by index

Options:
  -f, --force  Hyper-V gives the guest five minutes to save data, then forces
               a shutdown
  --help       Show this message and exit.
```
### pause
```
hypy pause --help
Usage: hypy.py pause [OPTIONS] INDEX

  Pause virtual machine identified by index

Options:
  --help  Show this message and exit.
```
### resume
```
hypy resume --help
Usage: hypy.py resume [OPTIONS] INDEX

  Resume (paused) virtual machine identified by index

Options:
  --help  Show this message and exit.
```
