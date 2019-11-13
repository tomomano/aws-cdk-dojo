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
pip install aws-cdk.aws-lambda aws-cdk.aws-apigateway aws-cdk.aws-dynamodb aws_cognito
```

## Create app.py

Copy and paste the following code in `app.py`.

```python
import os
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
    aws_apigateway as apigw,
    aws_cognito as cognito
)
```

Now, create a new stack by extending `core.Stack` class.

```python
class ApigatewayCognitoStack(core.Stack):

    def __init__(self, scope: core.App, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
```

### Create a Cognito user pool

First, we create a Cognito user pool.

```python
# create Cognito user pool
user_pool = cognito.UserPool(
    self, "testUserPool",
    auto_verified_attributes=[cognito.UserPoolAttribute.EMAIL],
    sign_in_type=cognito.SignInType.EMAIL
)
```

Let's customize the password policies:

```python
cfn_user_pool = user_pool.node.default_child
cfn_user_pool.policies = {
    "passwordPolicy": {
        "minimumLength": 8,
        "requireLowercase": True,
        "requireNumbers": True,
        "requireUppercase": True,
        "requireSymbols": False
    }
}
```

We also need to create an app client:

```python
# create pool client
pool_client = cognito.CfnUserPoolClient(
    self, 'testUserPoolClient',
    user_pool_id=user_pool.user_pool_id,
    supported_identity_providers=["COGNITO"],
    generate_secret=False,
    refresh_token_validity=1,
    explicit_auth_flows=["USER_PASSWORD"],
    allowed_o_auth_flows_user_pool_client=True,
    allowed_o_auth_flows=["implicit"],
    allowed_o_auth_scopes=["email", "openid", "aws.cognito.signin.user.admin"],
    callback_ur_ls=["http://localhost"],
    logout_ur_ls=["http://localhost"]
)
```

For the details of these parameters, read the [documentation](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-app-idp-settings.html).

### Create a API Gateway

Create REST API and add a resource named `/test`:

```python
# create REST API resource
api = apigw.RestApi(self, 'my_API')

# new resource - /test
test_resource = api.root.add_resource('test')
```

Then, we define a Cognito authorizer, using the user pool we've just define above:

```python
# Cognito authorizer
cfn_authorizer = apigw.CfnAuthorizer(
    self, "my_cognito",
    name='API_authorizer',
    type='COGNITO_USER_POOLS',
    identity_source='method.request.header.Authorization',
    rest_api_id=api.rest_api_id,
    provider_arns=[user_pool.user_pool_arn]
)
```

### Prepare Lambda handler

Create a directory named `lambda/` and add `handler.py` inside it with the following code:

```python
def handler(event, context):
    return { "statusCode": 200, "body": "Hellow world!" }
```

### Attach Lambda handler to the GET method

Using the simple python function defined above, we define a lambda function:

```python
# lambda handler
hello_world_handler = _lambda.Function(
   self, 'my_handler',
   code=_lambda.AssetCode('lambda'),
   handler='index.handler',
   runtime=_lambda.Runtime.PYTHON_3_7
)
```

Then attach this function with GET method, andd add our cognito authorizer:
```python
# attach GET method
hello_world_integration = apigw.LambdaIntegration(hello_world_handler)
meth = test_resource.add_method("GET", hello_world_integration,
    authorization_type=apigw.AuthorizationType.COGNITO
)
meth.node.find_child('Resource').add_property_override('AuthorizerId', cfn_authorizer.ref)
```

The AWS stack is complete now!

## Test

### Deploy app

First, let's deploy our app. Make sure that the stack builds without errors:
```bash
cdk synth
```
Then, deploy it to the AWS:
```bash
cdk deploy
```
(You may need to run `export AWS_ACCESS_KEY_ID=XXX` and `export AWS_SECRET_ACCESS_KEY=YYY` to specify your AWS account.)

At the end of the build, you will find the lines that would like this:

```bash
apigateway-cognito.PoolClientID = 42849fkokojdukrt8mxca91kdu
apigateway-cognito.myAPIEndpoint8B0EED61 = https://kasksdfq.execute-api.us-east-1.amazonaws.com/prod/
apigateway-cognito.UserPoolID = us-east-1_j3asdfa
```

Remember these parameters; we will use it later!

### Make sure that the API is protected
First, make sure that your api is indeed protected if you do not have right token to access.

Try
```
curl -iX GET '<YOUR API GATEWAY ENDPOINT>/test/'
```

As expected, you will get `401` errors:
```bash
HTTP/1.1 401 Unauthorized
```

### Create a test user

To test our API with tokens, we first need to create a test user.

You can do it in either in the web browser GUI or from the command line. Below I show the two methods. You can choose whichever you like.

#### Web browser GUI

(coming soon)

### Command line

Make sure that you have installed `AWS CLI` and set up correct credentials.

Then, run
```bash
aws cognito-idp sign-up --client-id <YOUR CLIENT ID> --username test@google.com --password randomPW2019
```

Replace `--client-id`, `--username` and `--password` with your own ones.

The newly created user must be "confirmed". To do it, run
```bash
aws cognito-idp admin-confirm-sign-up --user-pool-id <YOUR USER POOL ID> --username test@google.com
```

Replace `--user-pool-id` and `--username` with your own ones.

### Log in and get token

#### Web browser GUI

(coming soon)

#### Command line

To log in and obtain tokens, run
```bash
aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id <YOUR CLIENT ID> --auth-parameters USERNAME=test@google.com,PASSWORD=randomPW2019
```

Replace `--client-id`, `--username` and `--password` with your own ones.

If successful, the returned json will look like
```json
{
    "ChallengeParameters": {},
    "AuthenticationResult": {
        "AccessToken": "XXXX",
        "ExpiresIn": 3600,
        "TokenType": "Bearer",
        "RefreshToken": "YYY",
        "IdToken": "ZZZ"
    }
}
```

### Test API with right token
Run
```
curl -iX GET '<YOUR API GATEWAY ENDPOINT>/test/' -H 'Authorization: <ID TOKEN>'
```

Now you should get `200` response, and you will see a nice `Hellow world!` message.

That's it!