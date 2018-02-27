# HYPY - HYper-v in PYthon

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2d6d147eedc0403195262e6041537eb3)](https://www.codacy.com/app/avanzzzi/hypy?utm_source=github.com&utm_medium=referral&utm_content=avanzzzi/hypy&utm_campaign=badger)
[![Code Health](https://landscape.io/github/avanzzzi/hypy/master/landscape.svg?style=flat)](https://landscape.io/github/avanzzzi/hypy/master)

Multiplataform Hyper-V Manager using Python and FreeRDP

## How hypy works?
Hypy uses winrm or ssh to comunicate with hyper-v server shell and sends powershell commands to interact with the virtual machines. To access the virtual machines, hypy uses freeRDP.

## Hyper-V Server configuration
### Clients connecting via WinRM
Hypy uses winrm to communicate with the hyper-v host, so it must be enabled and accepting connections.
https://github.com/diyan/pywinrm has a session explaining how to enable WinRM on the server/remote host.

### Clients connecting via SSH
As an alternative to winrm, you can setup a SSH server on the hyper-v server. Using the protocol parameter in command line or setting ssh in the protocol option.

## Client configuration
### FreeRDP
FreeRDP binary must be in path (windows, linux and mac). Make sure FreeRDP is working before using hypy or it will not open the session to the virtual machine.

#### Linux: Your package manager should have freerdp 1.1.* avaiable or compile from source.
#### Mac: When using homebrew, make share to include --HEAD option to get the lastest version (1.1.*) with HyperV support or use macports. Either way you will need XCode installed.

Look into https://github.com/FreeRDP/FreeRDP for more instructions.

## Instalation
Hypy can be installed with pip
```
pip3 install git+https://github.com/avanzzzi/hypy.git@setup
```

## Configuration
To configure Hypy, create the file '~/.hypy.conf'. You can use hypy.conf.example that comes with the package to get a starting point or use the contents below.
These options can be overriden in the command line if needed.
```ini
[credentials]
host = <server name in domain>
domain = <domain name>
user = <user name in server>
pass = <password>

[options]
protocol = <ssh or winrm>
ssh_port = 22
sync_interval = <interval in hours to make new cache file>
```
## usage
```
hypy --help
Usage: hypy.py [OPTIONS] COMMAND [ARGS]...

  Multiplataform Hyper-V Manager using Python and FreeRDP

Options:
  -u, --user TEXT          Username in hyper-v server
  -p, --pass TEXT          Password in hyper-v server
  -d, --domain TEXT        Domain name
  -m, --host TEXT          Hyper-V server hostname/ip address
  -t, --proto [ssh|winrm]  Protocol to be used
  --help                   Show this message and exit.

Commands:
  connect  Connect to virtual machine identified by...
  create   Create a new snapshot with vm's current state
  delete   Delete a machine's snapshot by name
  list     List virtual machines and its indexes
  ls       List updated virtual machines and its indexes
  pause    Pause virtual machine identified by index
  restore  Restore virtual machine snapshot
  resume   Resume (paused) virtual machine identified by...
  save     Save virtual machine identified by index
  snaps    List virtual machine snapshots
  start    Start virtual machine identified by index
  stop     Stop virtual machine identified by index
```
If you need help on any subcommand, run `hypy.py COMMAND --help`

### list
Hypy will create a cache with indexes for each machine. These indexes are used by other hypy commands to interact with the virtual machines.
If your cache is older than the duration specified in sync_interval, a new cache will be created, so the machine's states will be updated.
To force an cache update use the sync parameter.
```
hypy list --help
Usage: hypy.py list [OPTIONS]

  List virtual machines and its indexes

Options:
  -s, --sync       Syncronize with server updating local cache
  -n, --name TEXT  Filter virtual machines by name
  --help           Show this message and exit.
```

A machine listing would look like this:
```
-- Hyper-V Virtual Machine Listing --
Index State   Name                           Uptime
[  0] saved   MACHINE 001                    0:00:00
[  1] saved   MACHINE 002                    0:00:00
[  2] running MACHINE 003                    1:23:46
[  3] running MACHINE 004                    9:01:33
[  4] paused  MACHINE 005                    34 days, 17:58:52
[  5] off     MACHINE 006                    0:00:00
[  6] running MACHINE 007                    23 days, 0:46:56
[  7] running MACHINE 008                    0:18:43
[  8] running MACHINE 009                    4 days, 2:16:29
[  9] off     MACHINE 010                    0:00:00
[ 10] off     MACHINE 011                    0:00:00
```
### ls
The hypy command `ls` is a shortcut to `list -s`
### connect
Hypy will check the vm state before connecting, starting it if necessary.
```
hypy connect --help
Usage: hypy.py connect [OPTIONS] IDENT

  Connect to virtual machine identified by index

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
### create
```
hypy create --help
Usage: hypy.py create [OPTIONS] IDENT SNAP_NAME

  Create a new snapshot with vm's current state

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
### delete
```
hypy delete --help
Usage: hypy.py delete [OPTIONS] IDENT SNAP_NAME

  Delete a machine's snapshot by name

Options:
  -n, --name  Use vm name instead of index
  -r          Remove snapshot's children as well
  --help      Show this message and exit.
```
### restore
```
hypy restore --help
Usage: hypy.py restore [OPTIONS] IDENT SNAP_NAME

  Restore virtual machine snapshot

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
### snaps
```
hypy snaps --help
Usage: hypy.py snaps [OPTIONS] IDENT

  List virtual machine snapshots

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
A snap listing would look like this, the `*` marks the current snapshot.
```
hypy snaps -n "MACHINE 001"
Index State   Name                           Uptime
[ 99] off     MACHINE 001                    0:01:00
-- Virtual Machine Snapshots --
MACHINE 001
 +-- snap_0* (01/01/2000 00:01:00)
     +-- snap_1 (05/02/2010 00:03:00)
```
### start
```
hypy start --help
Usage: hypy.py start [OPTIONS] IDENT

  Start virtual machine identified by index

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
### stop
```
hypy stop --help
Usage: hypy.py stop [OPTIONS] IDENT

  Stop virtual machine identified by index

Options:
  -f, --force  Hyper-V gives the guest five minutes to save data, then forces
               a shutdown
  -n, --name   Use vm name instead of index
  --help       Show this message and exit.
```
### pause
```
hypy pause --help
Usage: hypy.py pause [OPTIONS] IDENT

  Pause virtual machine identified by index

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
### resume
```
hypy resume --help
Usage: hypy.py resume [OPTIONS] IDENT

  Resume (paused) virtual machine identified by index

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
### save
```
hypy save --help
Usage: hypy.py save [OPTIONS] IDENT

  Save virtual machine identified by index

Options:
  -n, --name  Use vm name instead of index
  --help      Show this message and exit.
```
