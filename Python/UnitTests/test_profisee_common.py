import os, sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Common import Common

class unit_tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.node = {
            "key1": "value1",
            "key2": {
                "subkey1": "subvalue1"
            }
        }

    def test_get_existing_key(self):
        
        self.assertEqual(Common.Get(self.node, "key1"), "value1")
        self.assertEqual(Common.Get(self.node, "key2.subkey1"), "subvalue1")

    def test_get_non_existing_key(self):
        self.assertIsNone(Common.Get(self.node, "nonexistent"))
        self.assertIsNone(Common.Get(self.node, "key2.nonexistent"))

    def test_get_with_default(self):
        self.assertEqual(Common.Get(self.node, "nonexistent", default="default_value"), "default_value")
        self.assertEqual(Common.Get(self.node, "key2.nonexistent", default="default_value"), "default_value")

if __name__ == '__main__':
    unittest.main()