# Tutorial

Here, I demonstrate a simple CDK application with APIGateway authenticated by Cognito user pool.

## Initialize a project
Create a new directory where you will build your project:
```bash
$ mkdir apigateway_cognito
```

`cd` into it and initialize a CDK project:
```bash
$ cd apigateway_cognito
$ cdk init app --language=python
```
This command will create a directory named `api_cors_lambda_crud_dynamodb_stack`. Delete it, since we do not need it for now.

Then install dependencies by pip:
```bash
source .env/bin/activate
pip install -r requirements.txt
```

## Install aws-cdk modules
```bash
pip install aws-cdk.aws-lambda aws-cdk.aws-apigateway aws-cdk.aws-dynamodb
```

## Create app.py

Copy and paste the following code in `app.py`.

```python
from aws_cdk import core

from api_stack import ApigatewayCognitoStack

app = core.App()
ApigatewayCognitoStack(app, "apigateway-cognito")

app.synth()
```

This will be the entry point of your CDK app. As you can see, we are adding `ApigatewayCognitoStack` to our app.

Below, we will create `ApigatewayCognitoStack` stack!

## Create api_stack.py

Create a new python file named `api_stack.py` and open it with your editor.

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
class ApigatewayCognitoStack(core.Stack):

    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
```

Create REST API and add a resource (`/test`):

```python
# create REST API resource
api = apigw.RestApi(self, 'my_API')

# new resource - /test
test_resource = api.root.add_resource('test')
```

## Prepare Lambda handler

Create a directory named `lambda` and add `handler.py` inside it with the following code:

```python
def handler(event, context):
    return { "statusCode": 200, "body": "Hellow world!" }
```

## Attach Lambda handler to the GET method

```python
# lambda handler
hello_world_handler = _lambda.Function(
   self, 'my_handler',
   code=_lambda.AssetCode('lambda'),
   handler='index.handler',
   runtime=_lambda.Runtime.PYTHON_3_7
)

# attach GET method
hello_world_integration = apigw.LambdaIntegration(hello_world_handler)
test_resource.add_method("GET", hello_world_integration)
```

## Pause and test

Now is a good time to pause and test the code so far. First, check that your code builds by

```bash
cdk synth
```

Once you confirm it, deploy your stack by

```bash
cdk deploy
```

(You may need to run `export AWS_ACCESS_KEY_ID=` and `export AWS_SECRET_ACCESS_KEY=` to set your AWS account to deploy.)

Once the deploy finishes, you will find lines that would look like

```bash
Outputs:
apigateway-cognito.myAPIEndpoint8B0EED61 = https://qlkx3dwh238.execute-api.us-east-1.amazonaws.com/prod/
```

(Address will be different in your deployment.)

Test the API by using `curl`:

```bash
curl -iX GET https://qlkx3dwh238.execute-api.us-east-1.amazonaws.com/prod/
```

The API will return status code 200 and the message that says "Hello world!".

## Add Cognito authentication layer

Insert the following lines:

```
# Cognito authorizer
cfn_authorizer = apigw.CfnAuthorizer(
   self, "my_cognito",
   type='COGNITO_USER_POOLS',
   identity_source='method.request.header.Authorization',
   rest_api_id=api.rest_api_id,
   provider_arns=[cognito_arn]
)
```