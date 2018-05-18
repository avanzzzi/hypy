#!/usr/bin/env python3
# coding: utf-8
from hypy.cli_main import cli
from hypy.cli_snap import create, delete, restore, snap, snaps
from hypy.cli_switch import switch, switches

cli.add_command(switch)
cli.add_command(switches)

cli.add_command(snap)
cli.add_command(snaps)
cli.add_command(create)
cli.add_command(restore)
cli.add_command(delete)

cli()
