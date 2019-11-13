
# APIGateway with Cognito Authorizer

This stack shows an example to control access to a REST API using Amazon Cognito user pools as authorizer

Refs:
  * https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-integrate-with-cognito.html


## Requirements

* Python (>=3.7)
* AWS CDK (>=1.15)

## Install 

```python
python3 -m venv .env # or, python3.7 -m venv .env if default python is not 3.7
source .env/bin/activate
pip install -r requirements.txt
```

## Build
Synthesize the CloudFormation template by

```bash
cdk synth
```

## Deploy
(Optional) Set the account which you use to deploy the service:

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=ABCDEFGHIJK
```

To deploy the app, run

```bash
cdk deploy
```

## Clean up
When you're done with the stack, clean it up by
```bash
cdk destroy
```

## Test

### Deploy app

Deploy your app by

```bash
cdk deploy
```

At the end of the build, you will find the lines that would like this:

```bash
apigateway-cognito.PoolClientID = 1434jmfkokojdukrt8mxca91kdu
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

#### Command line

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