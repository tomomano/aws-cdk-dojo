
# APIGateway with CORS, Lambdas, and CRUD on DynamoDB
Original TypeScript code: https://github.com/aws-samples/aws-cdk-examples/tree/master/typescript/api-cors-lambda-crud-dynamodb


## Structure
  * `app.py`: This will be the main entry point of the app.
  * `api_cors_lambda_crud_dynamodb_stack.py`: This is the main stack of the app.

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

### cdk init
Create a new CDK project:
```bash
cdk init --language python
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


### Create a lambda function (POST)
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
        body = event["body"]
        if body is None:
            raise ValueError("invalid request, you are missing the parameter body")
        
        item = json.loads(body)
        item[PRIMARY_KEY] = uuid.uuid4().hex

        ddb = boto3.resource('dynamodb')
        table = ddb.Table(TABLE_NAME)
        response = table.put_item(Item=item)

        status_code = 200
        resp = response['Item']
    except Exception as e:
        status_code = 401
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

### Create API Gateway
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
You should get `200` status code, along with the newly created item.

### Add more APIs
The backbone of the application stack is finished now. Now you can add several more API methods.