# Author: Vilma Tomanová
# Date finished: 2025-27-11
# Description: Script for testing main.py with unit tests.
import unittest
from src.main import *

class TestMain(unittest.TestCase):
    def test_hash(self):
        self.assertEqual(sha256_password("heslo"),
                         "56b1db8133d9eb398aabd376f07bf8ab5fc584ea0b8bd6a1770200cb613ca005")

    def test_bad_input_hash(self):
        with self.assertRaises(TypeError):
            sha256_password(1), 0

    if __name__ == '__main__':
        unittest.main()