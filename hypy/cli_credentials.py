import click
from hypy.modules import config


@click.group('credentials', help='Generate or update the credentials file')
def credentials():
    """Manage config file of the Hyper-V Python."""
    pass


@credentials.command('create', help='Create hypy configuration file')
@click.option('--user', '-u', prompt=True, help='Username in hyper-v server')
@click.option('--passw', '-p', prompt=True, hide_input=True,
              help='Password in hyper-v server')
@click.option('--domain', '-d', prompt=True, help='Domain name')
@click.option('--host', '-m', prompt=True, help='Hyper-V server hostname/ip address')
@click.option('--proto', '-t', prompt=True, help='Protocol to be used',
              type=click.Choice(['ssh', 'winrm'], case_sensitive=False))
@click.option('--port', '-P', prompt=True, help='SSH port', default='22')
@click.option('--sync', '-s', prompt=True,
              help='Time, in hours, between autosync', default='2')
def generate_config_file(user, passw, domain, host, proto, port, sync):
    config.generate_credentials(user, passw, domain, host, proto, port, sync)


@credentials.command('update',
                     help='Update the password encryption of the hypy configuration file')
@click.option('--passw', '-p', prompt='Password. Blank keeps last password',
              hide_input=True, default='', help='Password in hyper-v server')
def update_password(passw):
    config.encrypt_password(passw)
