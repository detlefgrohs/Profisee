import os, sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
import json

class api_events_unit_tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        cls.profisee_settings = settings["Local"]

        cls.api = API(cls.profisee_settings["ProfiseeUrl"], cls.profisee_settings["ClientId"], verify_ssl=False)

    def test_call_external_event_notification(self):
        #response = self.api.GetAuthenticationURL()
        #self.assertEqual(self.api.StatusCode, 200)  # Not Implemented
        pass
    
    def test_cancel_unprocessed_event_messages(self):
        #response = self.api.GetAuthenticationURL()
        #self.assertEqual(self.api.StatusCode, 200)  # Not Implemented
        pass
    
    def test_trigger_internal_event(self):
        #response = self.api.GetAuthenticationURL()
        #self.assertEqual(self.api.StatusCode, 200)  # Not Implemented
        pass

if __name__ == '__main__':
    unittest.main()