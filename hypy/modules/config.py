"""
Hypy configuration manager module
"""
import configparser
from os.path import expanduser

CONFIG_FILE_LOCATION = expanduser('~/.hypy.conf')
configuration = None


def load(user: str, passw: str, domain: str, host: str, proto: str):
    """
    Read config file and command line to create the configuration.

    Args:
        user: User passed as command line option.
        passw: Password passed as command line option.
        domain: Domain passed as command line option.
        host: Host passed as command line option.
        proto: Protocol passed as command line option.
    """
    global configuration

    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_LOCATION)

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

        configuration['sync_interval'] = options['sync_interval']
        configuration['protocol'] = options['protocol']
        configuration['ssh_port'] = options['ssh_port']

        if proto is not None:
            configuration['protocol'] = proto

    except KeyError:
        print("Please, configure your credentials file - hypy.conf")
        print(CONFIG_FILE_LOCATION)
        exit(1)
