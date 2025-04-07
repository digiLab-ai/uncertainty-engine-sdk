openapi-generator generate \
  -g python \
  -i https://tu8vus047g.execute-api.eu-west-2.amazonaws.com/openapi.json \
  -c ./generate-client-config.json \
  --output uncertainty_engine/resource_api
