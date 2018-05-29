import sys
import unittest
from io import StringIO
from json import loads

from hypy.modules import printer
from tests.fixtures import snaps_json, snaps_tree


class TestPrinter(unittest.TestCase):

    def test_snaptree(self):
        out = StringIO()
        sys.stdout = out
        printer.print_vm_snaps(loads(snaps_json), "Virtual Machine", "snap 5")
        sys.stdout = sys.__stdout__
        self.assertEqual(snaps_tree, out.getvalue())
