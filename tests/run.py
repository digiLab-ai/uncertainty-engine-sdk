from pprint import pprint

from dotenv import load_dotenv

from uncertainty_engine.client import Client

ACCOUNT_ID = "67bf2b981deba2985079aed5"
PROJECT_ID = "67bf2b981deba2985079aed7"

load_dotenv()

client = Client(
    email="jasper",
    resource_deployment="https://tu8vus047g.execute-api.eu-west-2.amazonaws.com",
    deployment="https://07y3pw9ud1.execute-api.eu-west-2.amazonaws.com",
)

# client.authenticate(ACCOUNT_ID)

print("datasets:")
print(client.resources.list_resources(PROJECT_ID, "dataset"))

print("auth details:")
pprint(client.resources.auth_service.token.decoded_payload)
