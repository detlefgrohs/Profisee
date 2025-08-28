import logging, json, os
from Profisee import Restful

instance_name = "Local"

logging.basicConfig(filename = fr"{os.path.splitext(os.path.basename(__file__))[0]}.log", format="%(asctime)s %(levelname)s : %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.info(f"Running {__file__}")

with open('settings.json', 'r') as file: settings = json.load(file)
profisee_settings = settings[instance_name]

print(f"Connecting to '{profisee_settings["ProfiseeUrl"]}'")
logger.info(f"Connecting to '{profisee_settings["ProfiseeUrl"]}'")
api = Restful.API(profisee_settings["ProfiseeUrl"], profisee_settings["ClientId"], verify = False)

# print(api.RunConnectImmediate("MelissaData Personator Name Strategy", [ "100000000" ]))
# print(api.RunConnectImmediate("MelissaData Personator Name Strategy", [ "100000001" ]))

print(api.RunConnectBatch("MelissaData Personator Name Strategy"))
