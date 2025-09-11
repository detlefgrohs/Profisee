import argparse, json

class GenerateSQLDDL():
    
    def __init__(self, profisee_url: str, client_id: str, verify_ssl: bool) -> None:
        self.ProfiseeUrl = profisee_url
        self.ClientId = client_id
        self.VerifySSL = verify_ssl

    def generate(self) -> None:
        print(f"Connecting to '{self.ProfiseeUrl}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--instance", type=str, default="Local", help="The instance name to use from settings.json")
    args = parser.parse_args()
    
    instance_name = args.instance
    settings = json.load(open(r"settings.json"))[instance_name]
    
    profisee_url = settings.get("ProfiseeUrl", None)
    client_id = settings.get("ClientId", None)
    verify_ssl = settings.get("VerifySSL", True)
    
    print(f"Using instance '{instance_name}' with ProfiseeUrl '{profisee_url}', ClientId '{client_id}', VerifySSL '{verify_ssl}'")

    ddl_generator = GenerateSQLDDL(profisee_url, client_id, verify_ssl) 
    ddl_generator.generate()