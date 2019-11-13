
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




# Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
