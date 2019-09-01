
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
curl $ENDPOINT_ADDR/items/<ID VALUE> -iX PATCH -H "Content-Type: application/json" -d '{"age": 27}'

# Delete an item
curl $ENDPOINT_ADDR/items/<ID VALUE> -iX DELETE
```
## Structure
  * `app.py`: This will be the main entry point of the app.
  * `api_cors_lambda_crud_dynamodb_stack.py`: This is the main stack of the app.
  * `api/`: This is where lambda function handlers are defined.

## Commands
Set the account which you use to deploy the service:
```
$ export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
$ export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```

Synthesize:
```
cdk synth
```

Deploy:
```
cdk deploy
```

Clean up:
```
cdk destroy
```

## APIs
Post an object:
```bash
curl https://{APIGATEWAY ADDRESS}/prod/items -X POST -H "Content-Type: application/json" -d '{"name": "bob"}'
```


## Steps

### cdk initreturn { "statusCode": status_code, "body": json.dumps(resp) }
Create a new CDK project:
```bash
cdk init app --language python
```
This command will create a directory named `api_cors_lambda_crud_dynamodb_stack`. Delete it, since we do not need it for now.

Then install dependencies by pip:
```bash
source .env/bin/activate
pip install -r requirements.txt
```

### Install additional aws-cdk modules
```bash
pip install aws-cdk.aws-lambda aws-cdk.aws-apigateway aws-cdk.aws-dynamodb
```

### Create app.py
Copy and paste the following code in `app.py`:
```python
from aws_cdk import core

from api_stack import ApiLambdaCrudDynamoDBStack

app = core.App()
ApiLambdaCrudDynamoDBStack(app, "ApiLambdaCrudDynamoDBExample", env={'region': 'us-east-1'})

app.synth()
```

Below, we will create `ApiLambdaCrudDynamoDBExample` stack!

### Create api_stack.py
Create a new python file named `api_stack.py` and open it.

First, import cdk libraries that will be used in this stack:
```python
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    aws_apigateway as apg
)
```

Now, create a new stack by extending `core.Stack` class.
```python
class ApiLambdaCrudDynamoDBStack(core.Stack):

    def __init__(self, scope: core.Stack, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
```

### Create a DynamoDB table
API Reference: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_dynamodb/Table.html

To create a new dynamodb table, add the following lines to `__init__()` of `ApiLambdaCrudDynamoDBStack`:
```python
# create a dynamo db table
dynamo_table = ddb.Table(
   self, 'items',
   partition_key={
         'name': 'itemID',
         'type': ddb.AttributeType.STRING
   },
   table_name='items',
   removal_policy=core.RemovalPolicy.DESTROY # NOT recommended for production code
)
```

Now, to check everything has been working correctly so far, try deploying the stack by `cdk deploy` command. Go to the AWS Console, and check that a new DynamoDB table was actually created.


### Implementing POST method

#### Create a lambda function
Next, we will create a POST API unser `/items`.

First, create a new directory named `api/`. In there, create a lambda function handler named `create.py`, and paste the following code:
```python
import json, os
import uuid
import boto3

TABLE_NAME = os.environ.get('TABLE_NAME', '')
PRIMARY_KEY = os.environ.get('PRIMARY_KEY', '')

def handler(event, context):
    
    try:
        body = event.get("body", None)
        if body is None:
            raise ValueError("invalid request, you are missing the parameter body")
        
        item = json.loads(body)
        item[PRIMARY_KEY] = uuid.uuid4().hex

        ddb = boto3.resource('dynamodb')
        table = ddb.Table(TABLE_NAME)
        response = table.put_item(Item=item)

        status_code = 201
        resp = response['Item']
    
    except ValueError as e:
        status_code = 400
        resp = {"description": f"Bad request. {str(e)}"}
    
    except Exception as e:
        status_code = 500
        resp = {"description": str(e)}
    
    return { "statusCode": status_code, "body": json.dumps(resp) }
```

Then, define a Lambda function constructor for this function:
```python
# inside __init__()
create_one = _lambda.Function(
   self, 'createItemFunction',
   code=_lambda.AssetCode('api'),
   handler='create.handler',
   runtime=_lambda.Runtime.PYTHON_3_7,
   environment={
         "TABLE_NAME": dynamo_table.table_name,
         "PRIMARY_KEY": 'itemID'
   }
)
```

Lastly, do not forget to grant permission for this lambda function so that it can manipulate DynamoDB:
```python
dynamo_table.grant_read_write_data(create_one)
```

#### Create API Gateway
Now, let us connect the above Lambda function to API Gateway.

First, create a new API Gateway constructor:
```python
api = apigw.RestApi(
   self, 'itemsApi',
   rest_api_name="Items Service" # A name for the API Gateway RestApi resource
)
```
Then create a new resource:
```python
items = api.root.add_resource('items')
```
Then, attach POST method:
```python
create_one_integration = apigw.LambdaIntegration(create_one)
items.add_method('POST', create_one_integration)
```

Now, let's check the code so far. Deploy the stack by `cdk deploy` command. Find the address where API Gateway is deployed. Then, type the following CURL command:

```bash
curl https://{APIGATEWAY ADDRESS}/prod/items -i -X POST -H "Content-Type: application/json" -d '{"name": "bob"}'
```
You should get `201` status code, along with the newly created item info.

### Implementing GET
The backbone of the application stack is finished now. Now you can add several more API methods following the same procedure. First, let's add `GET` method. This method fetchs all items available in DB.

In `api_stack.py`, add the following lines:
```python
get_all_lambda = _lambda.Function(
            self, 'getAllItemsFunction',
            code=_lambda.AssetCode('api'),
            handler='get_all.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

# ...
dynamo_table.grant_read_write_data(get_all_lambda)

# ...
get_all_integration = apigw.LambdaIntegration(get_all_lambda)
items.add_method('GET', get_all_integration)
```

In addition, add a new lambda function handler, `get_all.py`.

Now let's run `cdk deploy` and check if the api works. Before running the below command, run several `POST` query to add some data in DB. Then,
```bash
curl https://{APIGATEWAY ADDRESS}/prod/items -iX GET
```
You should get a list of items in DB.

Now let's add GET method under `/items` resouce, which fetches a single item by specifying the ID.

In `api_stack.py`, add the following lines:
```python
get_one_lambda = _lambda.Function(
            self, 'getOneItemFunction',
            code=_lambda.AssetCode('api'),
            handler='get_one.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

# ...
dynamo_table.grant_read_write_data(get_one_lambda)

# ...
single_item = items.add_resource('{id}')
get_one_integration = apigw.LambdaIntegration(get_one_lambda)
single_item.add_method('GET', get_one_integration)
```

In addition, add a new lambda function handler, `get_one.py`.

Now run `cdk deploy` and test the method. First, make sure that you have some items in your DB, and make notes on the item's `itemID` value. Then, try the following curl command, with `{itemID}` replaced with an correct value.
```bash
curl https://{APIGATEWAY ADDRESS}/prod/items/{itemID} -iX GET
```
Did you get your desired item?

### Implementing DELETE and PATCH
Lastly, we implement DELETE and PATCH method. We basically repeat the same process as we did so far, so I do not explain much.

In `api_stack.py`, add the following lines:
```python
update_one = _lambda.Function(
            self, "updateItemFunction",
            code=_lambda.AssetCode('api'),
            handler='update_one.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

delete_one = _lambda.Function(
            self, 'deleteItemFunction',
            code=_lambda.AssetCode('api'),
            handler='delete_one.handler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            environment={
                "TABLE_NAME": dynamo_table.table_name,
                "PRIMARY_KEY": 'itemID'
            }
        )

# ...
dynamo_table.grant_read_write_data(update_one)
dynamo_table.grant_read_write_data(delete_one)

# ...
update_one_integration = apigw.LambdaIntegration(update_one)
single_item.add_method("PATCH", update_one_integration)

delete_one_integration = apigw.LambdaIntegration(delete_one)
single_item.add_method('DELETE', delete_one_integration)
```

In addition, add new lambda function handlers, `delete_one.py` and `update_one.py`.

Run `cdk deploy` and check your API with curl:
```bash
curl https://{APIGATEWAY ADDRESS}/prod/items/{itemID} -iX DELETE
curl https://{APIGATEWAY ADDRESS}/prod/items/{itemID} -iX PATCH -H "Content-Type: application/json" -d '{"age": 27}'
```
