import os, sys, uuid
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
from Profisee.Restful.Attribute import Attribute
from Profisee.Restful.Enums import AttributeDataType
import json

class attributes_unit_tests(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        profisee_settings = settings["Local"]
        cls.api = API(profisee_settings["ProfiseeUrl"], profisee_settings["ClientId"], verify_ssl=False)
        
    def test_get_attributes(self):
        response = self.api.GetAttributes()
        self.assertEqual(self.api.StatusCode, 200)

    def test_get_attributes_for_entity(self):
        response = self.api.GetAttributes("Test")
        self.assertEqual(self.api.StatusCode, 200)

    def test_get_attribute(self):
        response = self.api.GetAttribute("Test", "Name")
        self.assertEqual(self.api.StatusCode, 200)
        
    def test_create_attribute(self):
        new_attribute = Attribute("Test", f"NewAttribute_{uuid.uuid4()}", dataType=AttributeDataType.Number)
        new_attribute.Length = 0
        response = self.api.CreateAttribute(new_attribute.to_Attribute())
        self.assertEqual(self.api.StatusCode, 200)

if __name__ == '__main__':
    unittest.main()