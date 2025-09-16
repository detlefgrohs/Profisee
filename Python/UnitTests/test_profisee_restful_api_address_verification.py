import os, sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
import json

class address_verification_unit_tests(unittest.TestCase):
    # def __init__(self):
    #     super().__init__()
    #     self.test = "XYZ"
    
    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        profisee_settings = settings["Local"]
        cls.api = API(profisee_settings["ProfiseeUrl"], profisee_settings["ClientId"], verify_ssl=False)
        
    def test_get_strategies(self):
        response = self.api.GetAddressVerificationStrategies()
        self.assertEqual(self.api.StatusCode, 200)

    def test_get_strategy(self):
        self.assertTrue(True)

    def test_get_address_attributes(self):
        self.assertTrue(True)

    def test_start_strategy(self):
        self.assertTrue(True)

    def test_stop_strategy(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()