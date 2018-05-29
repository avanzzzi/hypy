import unittest
from collections import namedtuple
from json import loads

from hypy.modules import hvclient
from tests.fixtures import get_vm_response


class TestHVClient(unittest.TestCase):

    def test_parse_result(self):
        rs = namedtuple('Response', ['status_code', 'std_err', 'std_out'])
        rs.status_code = 0
        rs.std_err = 'err'
        rs.std_out = bytearray(get_vm_response.encode('latin-1'))

        self.assertEqual(hvclient.parse_result(rs), loads(get_vm_response))

    def test_parse_empty_response(self):
        rs = namedtuple('Response', ['status_code', 'std_err', 'std_out'])
        rs.status_code = 0
        rs.std_err = 'err'
        rs.std_out = ''

        self.assertIsNone(hvclient.parse_result(rs))

    def test_parse_error_response(self):
        rs = namedtuple('Response', ['status_code', 'std_err', 'std_out'])
        rs.status_code = 1
        rs.std_err = 'err'
        rs.std_out = 'out'

        with self.assertRaises(SystemExit) as cm:
            hvclient.parse_result(rs)

        self.assertEqual(cm.exception.code, 1)
