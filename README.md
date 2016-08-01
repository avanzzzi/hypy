# HYPY - HYper-v in PYthon
Multiplataform Hyper-V Manager using Python and FreeRDP

## How HYPY works?

Hypy uses winrm to comunicate with hyper-v server shell and sends powershell commands to interact with the virtual machines. Using Powershell, HYPY can get Name, ID and state of virtual machines. Therefore, HYPY call freeRDP with vm-id and credentials, using settings in `.conf` file to connect the vm.

## Configuration
to configure the Hypy you must change the file 'hypy.conf'
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

## usage
If you want use any functions and don't know parameters, you can use `hypy.py --help`
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
  restore  Restore virtual machine snapshot
  snaps    List virtual machine snapshots
  start    Start virtual machine identified by index
  stop     Stop virtual machine identified by index

```

### list
Now you know the parameters. For simulate the simple usage the first option is list: `hypy.py list` and Hypy list to you a machines for number:
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

The cache relates to 'list' option are saved in 'cache_file' and syncronize in fixed 'sync_interval' parameter.

for generate a new list before the sync_interval are a `-s` parameter.

example:
`./hypy.py list -s`

### connect

    ./hypy.py connect <number_of_list>
### create

    ./hypy.py create <number_of_list> <"name_of_snap">
### delete
If you needs delete a specific snapshop:

    ./hypy.py delete <number_of_list> <"name_of_snap">

if you need delete a snap trees:

    ./hypy.py delete -r <number_of_list> <"name_of_main_snap">
### restore

    ./hypy.py restore <number_of_list> <"name_of_snap">
### snaps

    ./hypy.py snaps <number_of_list>
### start

    ./hypy.py start <number_of_list>
### stop

    ./hypy.py stop <number_of_list>
