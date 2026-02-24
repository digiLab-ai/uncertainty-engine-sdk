from uncertainty_engine.client import Client

# Instantiate the client (adjust parameters as needed)
client = Client(env="dev")
client.authenticate()

# Test query_nodes with a simple query
nodes = client.query_nodes("Add")
print(nodes)
