import unittest
from main import Partfolio

class TestFilter(unittest.TestCase):
    def test_one_filter(self):
        try: Partfolio.interface()
        except: print("failed")

