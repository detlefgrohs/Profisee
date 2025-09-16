import os, sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
import json

class api_general_unit_tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        cls.profisee_settings = settings["Local"]

        cls.api = API(cls.profisee_settings["ProfiseeUrl"], cls.profisee_settings["ClientId"], verify_ssl=False)

    def test_properties(self):
        profisee_url = self.profisee_settings["ProfiseeUrl"]
        profisee_url = profisee_url if profisee_url.endswith("/") else f"{profisee_url}/"

        self.assertEqual(self.api.ProfiseeUrl, profisee_url)
        self.assertEqual(self.api.ClientId, self.profisee_settings["ClientId"])
        self.assertEqual(self.api.VerifySSL, self.profisee_settings["VerifySSL"])

if __name__ == '__main__':
    unittest.main()