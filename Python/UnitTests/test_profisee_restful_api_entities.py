import os, sys, uuid
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")))
from Profisee.Restful.API import API
from Profisee.Restful.Entity import Entity
import json

class entities_unit_tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'r') as file: settings = json.load(file)
        profisee_settings = settings["Local"]
        cls.api = API(profisee_settings["ProfiseeUrl"], profisee_settings["ClientId"], verify_ssl=False)

    def test_get_entities(self):
        response = self.api.GetEntities()
        self.assertEqual(self.api.StatusCode, 200)
                
    def test_create_entity(self):
        temp_entity_name = f"NewEntity_{str(uuid.uuid4())}"
        new_entity = Entity(temp_entity_name)
        new_entity.LongDescription = "This is a new entity created for unit testing."
        new_entity.IsCodeGenerationEnabled = True
        new_entity.CodeGenerationSeed = 100000000
        response = self.api.CreateEntity(new_entity.to_Entity())
        self.assertEqual(self.api.StatusCode, 200)

if __name__ == '__main__':
    unittest.main()