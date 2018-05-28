import unittest
from json import loads
from os import remove
from os.path import exists, join
from tempfile import gettempdir

from hypy.modules import cache

from test.fixtures import current_cache, get_vm_response, updated_cache


class TestCache(unittest.TestCase):

    def setUp(self):
        cache.current_host = 'test_host'
        self.cache_file = join(gettempdir(), 'vms_test_host.cache')
        if exists(self.cache_file):
            remove(self.cache_file)

    def test_cache_file(self):
        assert cache.get_cache_path() == self.cache_file

    def test_update_empty_cache(self):
        response = loads(get_vm_response)
        cache.update_cache(response)
        assert response == cache.list_vms()

    def test_update_cache(self):
        with open(self.cache_file, 'w') as fd:
            fd.write(current_cache)
        response = loads(get_vm_response)
        cache.update_cache(response)
        assert loads(updated_cache) == cache.list_vms()

    def test_invalid_cache(self):
        with open(self.cache_file, 'w') as fd:
            fd.write('[{}')
        assert not cache.list_vms()


if __name__ == '__main__':
    unittest.main()
