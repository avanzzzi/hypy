# HYPY - HYper-v in PYthon
Multiplataform Hyper-V Manager using Python and freeRDP

## How to HYPY woks?

Hypy use winrm to comunicate with hyper-v server shell And send powershell commands to interact with the virtual machines. Using Powershell HYPY can get Name, ID and state of virtual machines. Therefore, HYPY call freeRDP with vm-id and credentials, unset settings in the file `.conf` to connect in vm.

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
sync_interval = <interval in hours for make new cache file>
```

## usage
```python

```
