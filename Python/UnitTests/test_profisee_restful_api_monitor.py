import os, sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
from Profisee.Restful.Enums import ProcessActions
import json

class api_monitor_unit_tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        cls.profisee_settings = settings["Local"]

        cls.api = API(cls.profisee_settings["ProfiseeUrl"], cls.profisee_settings["ClientId"], verify_ssl=False)

    def test_get_monitor_activities(self):
        monitor_activities = self.api.GetMonitorActivities()
        self.assertGreater(len(monitor_activities), 0)
        self.assertEqual(self.api.StatusCode, 200)
        
    def test_get_monitor_activity(self):
        pass

    def test_get_monitor_activity_detail(self):
        pass

# Got a 405 when passing an empty string for the strategy name

if __name__ == '__main__':
    unittest.main()