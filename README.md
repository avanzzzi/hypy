# HYPY - HYper-v in PYthon

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2d6d147eedc0403195262e6041537eb3)](https://www.codacy.com/app/avanzzzi/hypy?utm_source=github.com&utm_medium=referral&utm_content=avanzzzi/hypy&utm_campaign=badger)
[![Code Health](https://landscape.io/github/avanzzzi/hypy/master/landscape.svg?style=flat)](https://landscape.io/github/avanzzzi/hypy/master)
[![Waffle.io - Columns and their card count](https://badge.waffle.io/avanzzzi/hypy.svg?columns=all)](https://waffle.io/avanzzzi/hypy)

Multiplatform Hyper-V Manager using Python and FreeRDP

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

## Install instructions
Hypy can be installed with pip
```
pip3 install git+https://github.com/avanzzzi/hypy.git
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

If you need help on any subcommand, run `hypy.py COMMAND --help`.
Further details on subcommands: https://github.com/avanzzzi/hypy/wiki
