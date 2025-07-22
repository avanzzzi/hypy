"""
Hypy configuration manager module
"""
import base64
import configparser
from os.path import expanduser

CONFIG_FILE_LOCATION = expanduser('~/.hypy.conf')
configuration = None


def encrypt_password(passw: str) -> None:
    """
    Update the password with a encrypted version of the passed in command line.

    Args:
        passw: Password passed as command line option.
    """
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_LOCATION)

        secret = config['credentials'].get('pass', '')

        if passw or not secret.startswith("b'"):
            config['credentials']['pass'] = str(base64.b64encode(passw.encode()))

            with open(CONFIG_FILE_LOCATION, 'w') as configfile:
                config.write(configfile)
    except KeyError:
        print("Please, configure your credentials file - hypy.conf")
        print(CONFIG_FILE_LOCATION)
        exit(1)


def generate_credentials(
    user: str,
    passw: str,
    domain: str,
    host: str,
    proto: str,
    ssh_port: str,
    sync_interval: str,
) -> None:
    """
    Generate config file from command line inputs create the configuration.

    Args:
        user: User passed as command line option.
        passw: Password passed as command line option.
        domain: Domain passed as command line option.
        host: Host passed as command line option.
        proto: Protocol passed as command line option.
        ssh_port: SSH port passed as command line option.
        sync_interval: Delay time between another sync (hours).
    """
    config = configparser.ConfigParser()
    config['credentials'] = {
        'user': user,
        'pass': str(base64.b64encode(passw.encode())),
        'domain': domain,
        'host': host,
    }
    config['options'] = {
        'sync_interval': sync_interval,
        'protocol': proto,
        'ssh_port': ssh_port,
    }

    with open(CONFIG_FILE_LOCATION, 'w') as configfile:
        config.write(configfile)


def load(
    user: str,
    passw: str,
    domain: str,
    host: str,
    proto: str,
) -> None:
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

        if not credentials.get('pass').startswith("b'"):
            encrypt_password(credentials.get('pass'))
            config.read(CONFIG_FILE_LOCATION)
            credentials = config['credentials']

        configuration = {'user': credentials['user'],
                         'pass': base64.b64decode(eval(credentials['pass'])),
                         'domain': credentials['domain'],
                         'host': credentials['host']}

        if user:
            configuration['user'] = user
        if passw:
            configuration['pass'] = passw
        if domain:
            configuration['domain'] = domain
        if host:
            configuration['host'] = host

        options = config['options']

        configuration['sync_interval'] = options['sync_interval']
        configuration['protocol'] = options['protocol']
        configuration['ssh_port'] = options['ssh_port']

        if proto:
            configuration['protocol'] = proto

    except KeyError:
        print("Please, configure your credentials file - hypy.conf")
        print(CONFIG_FILE_LOCATION)
        exit(1)
