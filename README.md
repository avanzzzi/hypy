# HYPY - HYper-v in PYthon
Multiplataform Hyper-V Manager using Python and FreeRDP

## How to HYPY woks?

Hypy uses winrm to comunicate with hyper-v server shell and sends powershell commands to interact with the virtual machines. Using Powershell HYPY can get Name, ID and state of virtual machines. Therefore, HYPY call freeRDP with vm-id and credentials, using settings in the file `.conf` to connect to vm.

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
```bash
hypy.py --help
```
