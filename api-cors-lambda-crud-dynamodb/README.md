
# APIGateway with CORS, Lambdas, and CRUD on DynamoDB
Original TypeScript code: https://github.com/aws-samples/aws-cdk-examples/tree/master/typescript/api-cors-lambda-crud-dynamodb

This is essentially a Python implementation of the above code.

## Build
```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```
Synthesize the CloudFormation template by
```bash
cdk synth
```

## Deploy
(Optional) Set the account which you use to deploy the service:
```bash
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```
To deploy the app, run
```bash
cdk deploy
```

When you are done with the app, do not forget to destroy it:
```bash
cdk destroy
```

## Test
You can play around with the deployed stack with the following command examples. Remember to replace `{ENDPOINT_ADDR}` with your own value, which you get once deployment is complete.

```bash
export ENDPOINT_ADDR="https://vbc8qgqwv7.execute-api.us-east-1.amazonaws.com/prod"

# Create an item in DB
curl $ENDPOINT_ADDR/items -iX POST -H "Content-Type: application/json" -d '{"name": "bob"}'

# Get all items in DB
curl $ENDPOINT_ADDR/items -iX GET

# Get a single item in DB by its itemID
curl $ENDPOINT_ADDR/items/<ID VALUE> -iX GET

# Update an item
curl $ENDPOINT_ADDR/items/<ID VALUE> -iX PATCH -H "Content-Type: application/json" -d '{"age": "27"}'

# Delete an item
curl $ENDPOINT_ADDR/items/<ID VALUE> -iX DELETE
```

## Structure
  * `app.py`: This will be the main entry point of the app.
  * `api_cors_lambda_crud_dynamodb_stack.py`: This is the main stack of the app.
  * `api/`: This is where lambda function handlers are defined.
  * `tutorial/`: A step-by-step tutorial is available here.