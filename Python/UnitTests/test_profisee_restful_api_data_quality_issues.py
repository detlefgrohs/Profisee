import os, sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
import json

class api_data_quality_issues_unit_tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        cls.profisee_settings = settings["Local"]

        cls.api = API(cls.profisee_settings["ProfiseeUrl"], cls.profisee_settings["ClientId"], verify_ssl=False)

    def test_get_data_quality_issues(self):
        # response = self.api.GetDataQualityIssues("EntityName", ["RecordCode1", "RecordCode2"], GetOptions())
        # self.assertEqual(self.api.StatusCode, 200)
        # self.assertIn("data", response)
        pass

if __name__ == '__main__':
    unittest.main()