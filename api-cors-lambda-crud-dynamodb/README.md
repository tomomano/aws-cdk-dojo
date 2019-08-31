
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

### app.py
Copy and paste the following code in `app.py`:
```python
from aws_cdk import core

from api_stack import ApiLambdaCrudDynamoDBStack

app = core.App()
ApiLambdaCrudDynamoDBStack(app, "my_api", env={'region': 'us-east-1'})

app.synth()
```

### ApiLambdaCrudDynamoDBStack
Create a new python file named `api_stack.py` and open it.

First, import cdk libraries:
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

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
```

### Create a DynamoDB table
API Reference: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_dynamodb/Table.html

Add the following lines to ApiLambdaCrudDynamoDBStack:
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

Then, try deploying the stack by `cdk deploy` command. Go to the AWS Console, and check that a new DynamoDB table was actually created.

