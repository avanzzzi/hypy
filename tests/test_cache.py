import unittest
from json import loads
from os import remove
from os.path import exists, join
from tempfile import gettempdir

from hypy.modules import cache

from tests.fixtures import current_cache, get_vm_response, updated_cache


class TestCache(unittest.TestCase):

    def setUp(self):
        cache.current_host = 'test_host'
        self.cache_file = join(gettempdir(), 'vms_test_host.cache')
        if exists(self.cache_file):
            remove(self.cache_file)

    def fill_cache(self):
        with open(self.cache_file, 'w') as fd:
            fd.write(current_cache)

    def test_cache_file(self):
        self.assertEqual(cache.get_cache_path(), self.cache_file)

    def test_update_empty_cache(self):
        response = loads(get_vm_response)
        cache.update_cache(response)
        self.assertEqual(response, cache.list_vms())

    def test_update_cache(self):
        self.fill_cache()
        response = loads(get_vm_response)
        cache.update_cache(response)
        self.assertEqual(loads(updated_cache), cache.list_vms())

    def test_invalid_cache(self):
        with open(self.cache_file, 'w') as fd:
            fd.write('[{}')
        self.assertIsNotNone(cache.list_vms())

    def test_get_by_name(self):
        self.fill_cache()
        vm = cache.get_vm_by_name('vm 01')
        self.assertEqual(vm['Id'], '01')

    def test_get_by_index(self):
        self.fill_cache()
        vm_name = cache.get_name(by_name=False, ident='1')
        self.assertEqual(vm_name, 'vm 03')
